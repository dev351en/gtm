import sys
from daytona import Daytona, DaytonaConfig

API_KEY = "your_daytona_api_key_here"
SANDBOX_ID = "b6a826ca-4dac-4716-b7b9-236b88b4718e"

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
