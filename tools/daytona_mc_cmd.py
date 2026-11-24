import os, sys
from daytona import Daytona, DaytonaConfig

sys.path.insert(0, os.path.dirname(__file__))
from credentials import get_daytona_api_key, get_daytona_sandbox_id

API_KEY = get_daytona_api_key()
SANDBOX_ID = get_daytona_sandbox_id()

def main():
    if len(sys.argv) < 2:
        print("Usage: python daytona_mc_cmd.py <command>")
        print("Example: python daytona_mc_cmd.py \"op PlayerName\"")
        sys.exit(1)
        
    cmd = " ".join(sys.argv[1:])
    client = Daytona(config=DaytonaConfig(api_key=API_KEY))
    s = client.v0.get(SANDBOX_ID)
    
    # Send keys into tmux minecraft session
    s.process.exec(f"tmux send-keys -t minecraft '{cmd}' Enter")
    
    # Wait a fraction and capture output
    import time
    time.sleep(1)
    res = s.process.exec("tmux capture-pane -pt minecraft")
    lines = res.result.strip().split("\n")
    print("\n--- Minecraft Console ---")
    for l in lines[-12:]:
        print(l)
    print("-------------------------")

if __name__ == "__main__":
    main()
