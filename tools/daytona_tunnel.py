import os, sys, time, subprocess
from daytona import Daytona, DaytonaConfig

API_KEY = "your_daytona_api_key_here"
SANDBOX_ID = "b6a826ca-4dac-4716-b7b9-236b88b4718e"

def main():
    print("=" * 65)
    print("      SDCRAFT - DAYTONA CLOUD MINECRAFT TUNNEL LAUNCHER")
    print("=" * 65)
    print("[1/3] Authenticating with Daytona Cloud API...")
    
    try:
        client = Daytona(config=DaytonaConfig(api_key=API_KEY))
        s = client.v0.get(SANDBOX_ID)
        print(f"      Connected to Sandbox: {SANDBOX_ID}")
        print(f"      Sandbox State: {s.state}")
        
        print("[2/3] Generating 24-hour secure SSH tunnel session...")
        ssh_info = s.create_ssh_access(expires_in_minutes=1440)
        token = ssh_info.token
        print(f"      Session Token: {token[:8]}... (Valid for 24 hours)")
        
        print("[3/3] Binding local port 25565 to Daytona Cloud server...")
        print("=" * 65)
        print("  >>> MINECRAFT IS READY TO CONNECT! <<<")
        print("  In Minecraft (Java Edition 26.3):")
        print("  Server Address: localhost:25565  (or 127.0.0.1:25565)")
        print("")
        print("  Live 3D BlueMap Web URL:")
        print("  https://8100-b6a826ca-4dac-4716-b7b9-236b88b4718e.daytonaproxy01.eu/")
        print("=" * 65)
        print("Tunnel is running. Keep this window open while playing.")
        print("Press Ctrl+C to disconnect.\n")
        
        cmd = f"ssh -N -L 25565:localhost:25565 -o StrictHostKeyChecking=no {token}@ssh.app.daytona.io"
        subprocess.run(cmd, shell=True)
        
    except KeyboardInterrupt:
        print("\nTunnel disconnected safely. Have a great day!")
    except Exception as e:
        print(f"\n[ERROR] Failed to start Daytona tunnel: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
