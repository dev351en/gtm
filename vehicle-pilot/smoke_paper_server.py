#!/usr/bin/env python3
"""One-time CI smoke test: private ephemeral Paper 26.3 server, no players."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
UA = {'User-Agent': 'GTM-Rickshaw-CI/0.1 (github.com/dev351en/gtm)'}

def load_json(url):
    with urlopen(Request(url, headers=UA), timeout=40) as response:
        return json.load(response)

def main():
    builds = load_json('https://fill.papermc.io/v3/projects/paper/versions/26.3/builds?channel=STABLE')
    build = next((x for x in builds if x.get('channel') == 'STABLE'), None)
    if not build:
        raise RuntimeError('No stable Paper 26.3 build available')
    entry = build['downloads']['server:default']
    print('Starting Paper 26.3 stable build', build['id'], flush=True)
    folder = ROOT / 'build/ephemeral-paper-server'
    folder.mkdir(parents=True, exist_ok=True)
    jar = folder / 'paper.jar'
    with urlopen(Request(entry['url'], headers=UA), timeout=180) as response:
        jar.write_bytes(response.read())
    if hashlib.sha256(jar.read_bytes()).hexdigest() != entry['checksums']['sha256']:
        raise RuntimeError('Official Paper binary checksum mismatch')
    (folder/'plugins').mkdir(exist_ok=True)
    src = next((ROOT/'build/libs').glob('*.jar'))
    shutil.copy2(src, folder/'plugins'/src.name)
    (folder/'eula.txt').write_text('eula=true\n', encoding='ascii')
    (folder/'server.properties').write_text(
        'online-mode=false\nserver-ip=127.0.0.1\nserver-port=25685\n'
        'white-list=true\nmax-players=1\nview-distance=4\n'
        'simulation-distance=3\nspawn-protection=0\n', encoding='ascii')
    log_path = folder/'paper-console.log'
    with log_path.open('w', encoding='utf-8') as log:
        proc = subprocess.Popen(['java','-Xms256M','-Xmx1024M','-jar','paper.jar','nogui'],
                                cwd=folder, stdin=subprocess.PIPE, stdout=log,
                                stderr=subprocess.STDOUT, text=True)
        ready = False
        try:
            for _ in range(155):
                time.sleep(1)
                text = log_path.read_text(encoding='utf-8',errors='replace')
                if 'Done (' in text and 'Rickshaw pilot ready:' in text:
                    ready = True
                    break
                if proc.poll() is not None:
                    break
            if not ready:
                raise RuntimeError('Plugin startup failed. Log tail:\n'+text[-6000:])
            print('PAPER_STARTUP_PASS: GTMVehiclePilot enabled on real Paper', flush=True)
        finally:
            if proc.poll() is None:
                try:
                    proc.stdin.write('stop\n')
                    proc.stdin.flush()
                    proc.wait(timeout=45)
                except Exception:
                    proc.kill()
                    proc.wait(timeout=15)
    if not ready or proc.returncode != 0:
        raise RuntimeError('Paper shutdown failed. Log tail:\n'+log_path.read_text(errors='replace')[-6000:])
    print(json.dumps({'paper_build':build['id'],
                      'status':'PAPER_STARTUP_PASS',
                      'live_vehicle_driving':'NOT_TESTED',
                      'foldcraft_4gb':'NOT_TESTED'}, indent=2))

if __name__=='__main__':
    main()
