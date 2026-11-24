import os, sys, time, subprocess, json, urllib.request
from daytona import Daytona, DaytonaConfig

sys.path.insert(0, os.path.dirname(__file__))
from credentials import get_daytona_api_key, get_daytona_sandbox_id, get_ngrok_authtoken

API_KEY = get_daytona_api_key()
SANDBOX_ID = get_daytona_sandbox_id()
NGROK_BIN = os.path.join(os.path.dirname(__file__), "ngrok", "ngrok.exe")

print("=" * 65)
print("      SDCRAFT - DAYTONA SERVER + NGROK MULTIPLAYER LAUNCHER")
print("=" * 65)

# 1. Connect to Daytona
print("[1/4] Connecting to Daytona Cloud server...")
client = Daytona(config=DaytonaConfig(api_key=API_KEY))
s = client.v0.get(SANDBOX_ID)
print(f"      Connected to Daytona Sandbox: {s.id} (Status: {s.state})")

# 2. Create Daytona SSH tunnel
print("[2/4] Initializing secure Daytona SSH tunnel...")
ssh_info = s.create_ssh_access(expires_in_minutes=1440)
token = ssh_info.token
print(f"      Token generated (Valid 24h)")

ssh_cmd = f"ssh -N -L 25565:localhost:25565 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o ServerAliveCountMax=3 {token}@ssh.app.daytona.io"
ssh_proc = subprocess.Popen(ssh_cmd, shell=True)
print("      SSH tunnel to Daytona started (PID: %d)" % ssh_proc.pid)
time.sleep(3)

# 3. Start Ngrok TCP tunnel
print("[3/4] Launching Ngrok TCP tunnel on port 25565...")
# Kill any existing ngrok
subprocess.run("taskkill /F /IM ngrok.exe 2>nul", shell=True)
time.sleep(1)

ngrok_proc = subprocess.Popen([NGROK_BIN, "tcp", "25565", "--log=stdout"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("      Ngrok started (PID: %d)" % ngrok_proc.pid)

# 4. Fetch public tunnel URL from Ngrok API
print("[4/4] Retrieving public multiplayer address...")
public_addr = None
for i in range(10):
    time.sleep(1)
    try:
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tunnels = data.get("tunnels", [])
            if tunnels:
                raw_url = tunnels[0].get("public_url", "")
                public_addr = raw_url.replace("tcp://", "")
                break
    except Exception:
        pass

print("\n" + "=" * 65)
if public_addr:
    print(" >>> SERVER IS ONLINE & ACCESSIBLE WORLDWIDE! <<<")
    print("=" * 65)
    print(f" 🌐 PUBLIC IP FOR YOUR FRIENDS:  {public_addr}")
    print(f" 💻 LOCAL IP FOR YOU:             localhost:25565")
    print("")
    print(" 🗺️ LIVE 3D BLUEMAP (BROWSER):")
    print("    https://8100-b6a826ca-4dac-4716-b7b9-236b88b4718e.daytonaproxy01.eu/")
    print("=" * 65)
    print("Keep this window open while playing with your friends!")
    print("Press Ctrl+C to disconnect anytime.\n")
    
    # Save active address to a text file for reference
    with open(r"d:\Games\SDCRAFT\ACTIVE_SERVER_ADDRESS.txt", "w") as f:
        f.write(f"PUBLIC ADDRESS FOR FRIENDS:\n{public_addr}\n\nLOCAL ADDRESS FOR YOU:\nlocalhost:25565\n\nBLUEMAP:\nhttps://8100-b6a826ca-4dac-4716-b7b9-236b88b4718e.daytonaproxy01.eu/\n")
else:
    print("[-] Could not retrieve Ngrok public address. Check if Ngrok is running.")

try:
    # Keep running until user stops
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down tunnels...")
    try:
        ssh_proc.terminate()
        ngrok_proc.terminate()
    except Exception:
        pass
    subprocess.run("taskkill /F /IM ngrok.exe 2>nul", shell=True)
    print("Disconnected safely.")
