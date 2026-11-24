import os, sys, subprocess
from daytona import Daytona, DaytonaConfig

sys.path.insert(0, os.path.dirname(__file__))
from credentials import get_daytona_api_key, get_daytona_sandbox_id

API_KEY = get_daytona_api_key()
SANDBOX_ID = get_daytona_sandbox_id()

def main():
    print("Connecting to Daytona VPS Linux Shell...")
    client = Daytona(config=DaytonaConfig(api_key=API_KEY))
    s = client.v0.get(SANDBOX_ID)
    ssh_info = s.create_ssh_access(expires_in_minutes=1440)
    token = ssh_info.token
    
    cmd = f"ssh -t -o StrictHostKeyChecking=no {token}@ssh.app.daytona.io \"cd /home/daytona/sdcraft_server && exec zsh\""
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()
