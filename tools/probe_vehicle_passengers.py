#!/usr/bin/env python3
"""Bounded four-player vehicle acceptance probe for the isolated Paper26.3 copy.

This uses real network Player sessions and ordinary register/login. It validates
pack bytes and sends headless resource-pack acknowledgements; it does NOT render
Minecraft and must never be described as four-client visual verification.
Credentials exist only in memory. No operator grants, block/world edits, forced
mounts, private-world access, or changes to the GUI observer are performed.
"""
from __future__ import annotations
import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import re
import secrets
import socket
import struct
import threading
import time
import urllib.parse
import urllib.request
import uuid
from zipfile import ZipFile
import zlib

FIXTURE = Path(__file__).with_name("fixtures") / "paper26_3_protocol777.json"
MAX_PACKET = 16 * 1024 * 1024


def varint(value):
    value &= 0xffffffff
    out = bytearray()
    while True:
        part = value & 127
        value >>= 7
        out.append(part | (128 if value else 0))
        if not value:
            return bytes(out)


def text_bytes(value):
    data = value.encode("utf-8")
    return varint(len(data)) + data


class Reader:
    def __init__(self, data): self.data, self.at = data, 0
    def take(self, count):
        if count < 0 or self.at + count > len(self.data): raise ValueError("Truncated packet")
        value = self.data[self.at:self.at+count]; self.at += count; return value
    def number(self, fmt): return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]
    def var(self):
        value = 0
        for shift in range(0,35,7):
            part = self.number(">B"); value |= (part & 127) << shift
            if not part & 128: return value
        raise ValueError("Oversized VarInt")
    def string(self):
        count = self.var()
        if count > MAX_PACKET: raise ValueError("Oversized text")
        return self.take(count).decode("utf-8")
    def nbt_string(self): return self.take(self.number(">H")).decode("utf-8")
    def nbt(self, kind=None, depth=0):
        if depth > 64: raise ValueError("NBT depth exceeded")
        kind = self.number(">B") if kind is None else kind
        if kind == 0: return None
        if kind in {1,2,3,4,5,6}: return self.number({1:">b",2:">h",3:">i",4:">q",5:">f",6:">d"}[kind])
        if kind == 8: return self.nbt_string()
        if kind in {7,11,12}:
            length = self.number(">i")
            if length < 0 or length > MAX_PACKET: raise ValueError("NBT array size")
            return self.take(length * {7:1,11:4,12:8}[kind])
        if kind == 9:
            child, length = self.number(">B"), self.number(">i")
            if length < 0 or length > 100000: raise ValueError("NBT list size")
            return [self.nbt(child,depth+1) for _ in range(length)]
        if kind == 10:
            result = {}
            while True:
                child = self.number(">B")
                if child == 0: return result
                key = self.nbt_string(); result[key] = self.nbt(child,depth+1)
        raise ValueError("Unknown NBT kind")


def component_text(value):
    if isinstance(value,str): return value
    if isinstance(value,list): return "".join(component_text(v) for v in value)
    if isinstance(value,dict):
        return "".join(component_text(value[k]) for k in ("text","translate","with","extra") if k in value)
    return ""


class Probe:
    def __init__(self, root, output, hold_mounted=0):
        self.root, self.output = root.resolve(), output
        if not 0 <= hold_mounted <= 60:
            raise ValueError("Mounted screenshot interval must be within0–60seconds")
        self.hold_mounted = hold_mounted
        self.fixtures = json.loads(FIXTURE.read_text())
        properties = dict(line.split("=",1) for line in (root/"server.properties").read_text().splitlines() if "=" in line and not line.startswith("#"))
        if properties.get("server-ip") != "127.0.0.1" or properties.get("server-port") != "25585":
            raise ValueError("Probe accepts only the explicitly isolated127.0.0.1:25585 server")
        config = (root/"plugins/SDCraftCore/config.yml").read_text()
        if not re.search(r"(?m)^local-playtest:\s*\n  profile: public_local_workshop_v1\s*$", config):
            raise ValueError("Missing isolated public workshop profile")
        with ZipFile(root/"versions/26.3/paper-26.3.jar") as jar:
            for path, expected in self.fixtures["classes_sha256"].items():
                if hashlib.sha256(jar.read(path)).hexdigest() != expected:
                    raise ValueError("Unknown Paper protocol registration; refusing guessed packets")
        self.token = (root/"plugins/SDCraftCore/console-access.token").read_text().strip()
        self.http = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        self.bots, self.allowed_names, self.pack_cache = [], set(), {}
        self.pack_lock = threading.Lock()
        cores = list((root/"plugins").glob("SDCraftCore*.jar"))
        if len(cores) != 1:
            raise ValueError("Expected exactly one active staged SDCraftCore JAR")
        self.report = {"schema":"GTM_VEHICLE_NETWORK_PLAYERS_V1", "status":"RUNNING", "protocol":777,
                       "started_utc":datetime.now(timezone.utc).isoformat(),
                       "core_sha256":hashlib.sha256(cores[0].read_bytes()).hexdigest(),
                       "environment":"isolated public-workshop Paper26.3; ordinary unprivileged network Player accounts",
                       "visual_verification":False,
                       "pack_status_scope":"Downloaded SHA1 and ZIP integrity verified; SUCCESSFULLY_LOADED is a headless protocol ACK, not rendering evidence.",
                       "checks":[], "observations":{}}
        self.save()

    def save(self):
        self.output.parent.mkdir(parents=True,exist_ok=True)
        temporary = self.output.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.report,indent=2)+"\n"); temporary.replace(self.output)

    def status(self):
        request=urllib.request.Request("http://127.0.0.1:8765/api/status",headers={"Authorization":"Bearer "+self.token})
        with self.http.open(request,timeout=4) as response: return json.load(response)

    def wait(self, label, predicate, timeout=20):
        end = time.monotonic()+timeout
        while time.monotonic() < end:
            for bot in self.bots:
                if not bot.closed and bot.error: raise RuntimeError(label+": "+bot.error)
            value=predicate()
            if value: return value
            time.sleep(.15)
        raise RuntimeError("Timed out: "+label)

    def check(self, name, detail=None):
        row={"check":name,"status":"PASS"}
        if detail is not None: row["detail"]=detail
        self.report["checks"].append(row); self.save()

    def connect(self, name, password=None):
        self.allowed_names.add(name)
        bot=Bot(self,name,password or secrets.token_hex(16));self.bots.append(bot);bot.start()
        self.wait("play protocol for "+name,lambda:bot.entity_id is not None and bot.position is not None,40)
        bot.command(("login "+bot.password) if password else ("register "+bot.password+" "+bot.password))
        account=self.wait("ordinary account authentication for "+name,
                  lambda:next((p for p in self.status()["players"] if p["name"]==name and p["authenticated"]),None),25)
        bot.account_uuid=str(uuid.UUID(account["uuid"]))
        return bot

    def place(self, bot, position):
        if bot.name not in self.allowed_names or not re.fullmatch(r"GTMSeat[0-9a-f]{8}[D1234]",bot.name):
            raise ValueError("Only this probe's test accounts may be positioned")
        if not all(math.isfinite(x) for x in position[:3]): raise ValueError("Invalid observed position")
        command="tp "+bot.name+" "+" ".join(format(v,".4f") for v in position[:3])+" 0 0"
        request=self.root/"control"/("command-vehicle-probe-"+secrets.token_hex(6)+".json")
        request.write_text(json.dumps({"command":command}))
        self.wait("position test player at observed safe starting point",lambda:not request.exists(),5)
        time.sleep(.3)

    def pack(self, url, expected):
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!="http" or parsed.hostname!="127.0.0.1" or parsed.port!=25586 or parsed.path!="/gtm-pack.zip":
            raise ValueError("Unexpected isolated pack endpoint")
        with self.pack_lock:
            if expected in self.pack_cache: return
            with self.http.open(url,timeout=20) as response: data=response.read(40*1024*1024+1)
            if len(data)>40*1024*1024 or hashlib.sha1(data).hexdigest()!=expected:
                raise ValueError("Headless pack hash validation failed")
            with ZipFile(BytesIO(data)) as archive:
                if archive.testzip() is not None or "pack.mcmeta" not in archive.namelist():
                    raise ValueError("Headless pack integrity validation failed")
            self.pack_cache[expected] = hashlib.sha256(data).hexdigest()

    def positions(self, bots):
        current={p["name"]:p for p in self.status()["players"]}
        return {b.name:[current[b.name][k] for k in ("x","y","z")] for b in bots}

    def run(self):
        initial=self.status()
        if initial.get("maxPlayers",0)-len(initial["players"]) < 5:
            raise RuntimeError("Five free staging player slots are required; keep GUI observer separate")
        suffix=secrets.token_hex(4)
        driver=self.connect("GTMSeat"+suffix+"D")
        origin=driver.position
        self.check("Ordinary driver registration and authenticated session")
        # The maintained plugin's grantNativeStarter uses this exact durable
        # name-UUID receipt. Target our own grant, never a nearby observer's car.
        receipt=uuid.UUID(bytes=hashlib.md5(("gtm:starter-auto:v1:"+driver.account_uuid).encode()).digest(),version=3)
        marker=driver.message_count
        driver.command("car info "+str(receipt))
        vehicle=self.wait("owned nearby starter auto identity",lambda:driver.vehicle_info_since(marker),20)
        if "Indra Auto" not in vehicle[1]: raise RuntimeError("Starter vehicle is not the repaired traditional auto")
        vehicle_id=vehicle[0]
        if vehicle_id!=str(receipt): raise RuntimeError("Observed vehicle is not this probe driver's starter receipt")
        self.report["observations"].update({"vehicle":vehicle_id,"driver":driver.name,"safe_start_position":origin[:3]})
        passengers=[self.connect("GTMSeat"+suffix+str(i)) for i in range(1,4)]
        overflow=self.connect("GTMSeat"+suffix+"4")
        for bot in [*passengers,overflow]: self.place(bot,origin)
        self.check("Four guest accounts registered without operator grants")
        passengers[0].command("car passenger "+vehicle_id)
        self.wait("locked guest admission rejected",lambda:passengers[0].has_message("Vehicle is locked"))
        if passengers[0].mount is not None: raise RuntimeError("Locked guest mounted unexpectedly")
        self.check("Owner lock rejects an ordinary guest")
        driver.command("car enter "+vehicle_id)
        driver_carrier=self.wait("driver mounting",lambda:driver.mount)
        driver.command("car lock "+vehicle_id)
        self.wait("owner unlock",lambda:driver.has_message("Passenger access unlocked"))
        for bot in passengers:
            bot.command("car passenger "+vehicle_id)
            self.wait("passenger mounting "+bot.name,lambda b=bot:b.mount)
        all_riders=[driver,*passengers]
        mounts=[b.mount for b in all_riders]
        if len(set(mounts)) != 4: raise RuntimeError("Four unique actual player seat carriers were not observed")
        self.report["observations"]["four_player_carriers"]={b.name:b.mount for b in all_riders}
        self.check("Driver plus three real Player network sessions simultaneously mounted",{"distinct_carriers":4})
        if self.hold_mounted:
            self.report["phase"]="four_occupants_mounted_for_optional_gui_observation";self.save()
            deadline=time.monotonic()+self.hold_mounted
            while time.monotonic()<deadline:
                if any(b.error for b in all_riders): raise RuntimeError("A mounted test connection ended during the observation interval")
                time.sleep(.2)
            self.report.pop("phase",None);self.save()
        overflow.command("car passenger "+vehicle_id)
        self.wait("full vehicle rejection",lambda:overflow.has_message("No requested seat is free"))
        if overflow.mount is not None: raise RuntimeError("Fifth rider incorrectly mounted")
        overflow.close();self.check("Fifth rider rejected while all four seats are occupied")
        time.sleep(1.2)
        before=self.positions(all_riders)
        driver.input(1);time.sleep(1.8);driver.input(16);time.sleep(.6);driver.input(0)
        time.sleep(1.2)
        after=self.positions(all_riders)
        movement={b.name:[after[b.name][i]-before[b.name][i] for i in range(3)] for b in all_riders}
        if any(math.hypot(d[0],d[2])<1 for d in movement.values()):
            raise RuntimeError("All four players did not measurably follow the driven vehicle; inspect actual obstructions")
        if [b.mount for b in all_riders]!=mounts: raise RuntimeError("Passenger attachment changed during driving")
        reference=movement[driver.name]
        if any(abs(d[i]-reference[i])>1 for d in movement.values() for i in range(3)):
            raise RuntimeError("Passengers did not follow the same accepted vehicle displacement")
        self.check("All four occupants follow actual driver input and brake together",{"block_displacements":movement})
        passengers[0].command("car exit")
        self.wait("safe passenger exit",lambda:passengers[0].mount is None)
        if driver.mount!=driver_carrier: raise RuntimeError("Passenger exit removed the driver")
        passengers[0].command("car enter "+vehicle_id)
        self.wait("automatic guest reboarding",lambda:passengers[0].mount)
        if passengers[0].mount==driver_carrier: raise RuntimeError("Guest acquired the driver's seat")
        self.check("Passenger safe exit and automatic reboarding preserve driver ownership")
        previous=passengers[1];name,password,carrier=previous.name,previous.password,previous.mount
        previous.close();time.sleep(1)
        rejoined=self.connect(name,password)
        self.place(rejoined,origin)
        rejoined.command("car passenger "+vehicle_id)
        self.wait("reconnected player can reuse released seat",lambda:rejoined.mount)
        if rejoined.mount!=carrier: raise RuntimeError("Disconnected passenger seat was not released/reused")
        passengers[1]=rejoined;all_riders=[driver,*passengers]
        self.check("Quit releases passenger occupancy; ordinary login reclaims the free seat")
        driver.command("car park "+vehicle_id)
        self.wait("parking safely exits every occupant",lambda:all(b.mount is None for b in all_riders))
        self.check("Park safely exits all four actual Player occupants")
        self.report["observations"]["pack_sha256_by_sha1"]=self.pack_cache
        self.report["status"]="PASS"

    def finish(self):
        for bot in self.bots: bot.close()
        self.report["credential_retention"]="None: random test passphrases remained in process memory and are not in this report."
        self.report["world_scope"]="Only disposable staging accounts/ordinary starter records and player movement; no world blocks, production files or GUI observer were changed."
        self.report["finished_utc"]=datetime.now(timezone.utc).isoformat()
        self.token="";self.save()


class Bot:
    def __init__(self,probe,name,password):
        self.probe,self.name,self.password=probe,name,password
        self.state,self.compression="login",-1
        self.entity_id,self.position=None,None
        self.passengers={};self.messages=deque(maxlen=150);self.message_count=0
        self.lock,self.send_lock=threading.RLock(),threading.Lock()
        self.error=None;self.closed=False;self.sock=None
        self.ids=probe.fixtures["states"]

    @property
    def mount(self):
        with self.lock:
            return next((entity for entity,people in self.passengers.items() if self.entity_id in people),None)

    def has_message(self,needle):
        with self.lock: return any(needle in text for _,text in self.messages)

    def vehicle_info_since(self,marker):
        with self.lock:
            for index,text in self.messages:
                if index<=marker or "energy" not in text or "health" not in text: continue
                match=re.search(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}",text)
                if match: return match[0],text
        return None

    def start(self):
        self.sock=socket.create_connection(("127.0.0.1",25585),timeout=5);self.sock.settimeout(1)
        self.send_packet(0,varint(777)+text_bytes("127.0.0.1")+struct.pack(">H",25585)+varint(2))
        identity=uuid.UUID(bytes=hashlib.md5(("OfflinePlayer:"+self.name).encode()).digest(),version=3)
        self.send_packet(0,text_bytes(self.name)+identity.bytes)
        threading.Thread(target=self.read_loop,daemon=True).start()

    def send_packet(self,packet_id,data=b""):
        payload=varint(packet_id)+data
        with self.send_lock:
            if self.compression>=0:
                payload=(varint(len(payload))+zlib.compress(payload)) if len(payload)>=self.compression else b"\0"+payload
            self.sock.sendall(varint(len(payload))+payload)

    def send(self,name,data=b"",state=None):
        self.send_packet(self.ids[state or self.state]["SERVERBOUND"]["SERVERBOUND_"+name],data)

    def command(self,value): self.send("CHAT_COMMAND",text_bytes(value),"play")
    def input(self,value): self.send("PLAYER_INPUT",bytes([value]),"play")

    def receive(self,count):
        data=bytearray()
        while len(data)<count and not self.closed:
            try: part=self.sock.recv(count-len(data))
            except socket.timeout: continue
            if not part: raise EOFError("Server closed test connection")
            data.extend(part)
        if len(data)!=count: raise EOFError("Test connection closed")
        return bytes(data)

    def packet(self):
        length=0
        for shift in range(0,35,7):
            value=self.receive(1)[0];length|=(value&127)<<shift
            if not value&128: break
        else: raise ValueError("Oversized frame length")
        if length>MAX_PACKET: raise ValueError("Oversized frame")
        data=self.receive(length)
        if self.compression>=0:
            envelope=Reader(data);size=envelope.var();raw=envelope.take(len(data)-envelope.at)
            if size>MAX_PACKET: raise ValueError("Oversized compressed frame")
            if size:
                inflater=zlib.decompressobj();data=inflater.decompress(raw,MAX_PACKET+1)
                if len(data)>MAX_PACKET or not inflater.eof: raise ValueError("Compressed frame exceeds bound")
            else: data=raw
            if size and len(data)!=size: raise ValueError("Compressed frame length mismatch")
        payload=Reader(data);packet_id=payload.var()
        name=next((k for k,v in self.ids[self.state]["CLIENTBOUND"].items() if v==packet_id),"UNKNOWN")
        return name,payload

    def settings(self):
        self.send("CLIENT_INFORMATION",text_bytes("en_us")+bytes([2])+varint(0)+bytes([1,127])+varint(1)+bytes([0,1])+varint(0))

    def read_loop(self):
        name="initial"
        try:
            while not self.closed:
                name,p=self.packet()
                if self.state=="login":
                    if name=="CLIENTBOUND_LOGIN_COMPRESSION": self.compression=p.var()
                    elif name=="CLIENTBOUND_LOGIN_FINISHED":
                        self.send("LOGIN_ACKNOWLEDGED");self.state="config";self.settings()
                    elif name=="CLIENTBOUND_CUSTOM_QUERY": self.send("CUSTOM_QUERY_ANSWER",varint(p.var())+b"\0")
                    elif name=="CLIENTBOUND_HELLO": raise RuntimeError("Isolated probe will not authenticate online accounts")
                    elif name=="CLIENTBOUND_LOGIN_DISCONNECT": raise RuntimeError("Server refused isolated test login")
                if name=="CLIENTBOUND_COOKIE_REQUEST": self.send("COOKIE_RESPONSE",text_bytes(p.string())+b"\0")
                elif name=="CLIENTBOUND_KEEP_ALIVE": self.send("KEEP_ALIVE",p.take(8))
                elif name=="CLIENTBOUND_PING": self.send("PONG",p.take(4))
                elif name=="CLIENTBOUND_DISCONNECT":
                    reason=component_text(p.nbt()).replace(self.password,"[redacted]")
                    raise RuntimeError("Server disconnected test player: "+reason[:160])
                elif name=="CLIENTBOUND_TRANSFER": raise RuntimeError("Probe refuses server transfers")
                elif name=="CLIENTBOUND_CODE_OF_CONDUCT": raise RuntimeError("Unexpected code-of-conduct gate requires manual review")
                elif name=="CLIENTBOUND_SELECT_KNOWN_PACKS": self.send("SELECT_KNOWN_PACKS",varint(0))
                elif name=="CLIENTBOUND_RESOURCE_PACK_PUSH":
                    pack_id,url,sha=p.take(16),p.string(),p.string()
                    self.send("RESOURCE_PACK",pack_id+varint(3))
                    self.probe.pack(url,sha)
                    self.send("RESOURCE_PACK",pack_id+varint(4));self.send("RESOURCE_PACK",pack_id+varint(0))
                elif name=="CLIENTBOUND_FINISH_CONFIGURATION":
                    self.send("FINISH_CONFIGURATION");self.state="play"
                elif name=="CLIENTBOUND_START_CONFIGURATION":
                    self.send("CONFIGURATION_ACKNOWLEDGED");self.state="config";self.settings()
                elif self.state=="play":
                    if name=="CLIENTBOUND_LOGIN":
                        self.entity_id=p.number(">i");self.send("PLAYER_LOADED")
                    elif name=="CLIENTBOUND_PLAYER_POSITION":
                        teleport=p.var();values=[p.number(">d") for _ in range(6)];yaw,pitch=p.number(">f"),p.number(">f");flags=p.number(">i")
                        old=self.position or (0,0,0,0,0)
                        pos=[values[i]+(old[i] if flags&(1<<i) else 0) for i in range(3)]
                        yaw+=old[3] if flags&8 else 0;pitch+=old[4] if flags&16 else 0
                        self.position=(*pos,yaw,pitch)
                        self.send("ACCEPT_TELEPORTATION",varint(teleport))
                        self.send("MOVE_PLAYER_POS_ROT",struct.pack(">dddffB",*self.position,1))
                    elif name=="CLIENTBOUND_CHUNK_BATCH_FINISHED": self.send("CHUNK_BATCH_RECEIVED",struct.pack(">f",4))
                    elif name=="CLIENTBOUND_SET_PASSENGERS":
                        entity,count=p.var(),p.var()
                        if count>64: raise ValueError("Unexpected passenger count")
                        people=[p.var() for _ in range(count)]
                        with self.lock: self.passengers[entity]=people
                    elif name=="CLIENTBOUND_SYSTEM_CHAT":
                        value=component_text(p.nbt()).replace(self.password,"[redacted]")
                        with self.lock:
                            self.message_count+=1;self.messages.append((self.message_count,value))
        except Exception as failure:
            if not self.closed: self.error=name+": "+str(failure).replace(self.password,"[redacted]")[:220]

    def close(self):
        if self.closed: return
        self.closed=True
        if self.sock:
            try: self.sock.shutdown(socket.SHUT_RDWR)
            except OSError: pass
            self.sock.close()
        self.password=""


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    parser.add_argument("--hold-mounted",default=0,type=int,help="Optional0–60second interval with four seats occupied for an independent GUI observer")
    args=parser.parse_args()
    probe=None
    try:
        probe=Probe(args.server,args.output,args.hold_mounted);probe.run()
    except Exception as failure:
        if probe:
            probe.report["status"]="FAIL";probe.report["failure"]=str(failure)
        else:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps({"status":"BLOCKED","failure":str(failure)},indent=2)+"\n")
        print("Vehicle network-player probe did not pass; inspect its bounded report.")
        return 1
    finally:
        if probe: probe.finish()
    print("Vehicle network-player probe passed; headless state checks, not visual certification.")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
