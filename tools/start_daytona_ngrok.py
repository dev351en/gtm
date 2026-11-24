import os, sys, time, json
from daytona import Daytona, DaytonaConfig

API_KEY = "your_daytona_api_key_here"
SANDBOX_ID = "b6a826ca-4dac-4716-b7b9-236b88b4718e"

token_file = os.path.join(os.path.dirname(__file__), "ngrok_authtoken.txt")

def get_token():
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            t = f.read().strip()
            if t:
                return t
    print("=" * 65)
    print("         NGROK AUTHTOKEN REQUIRED FOR TCP TUNNEL")
    print("=" * 65)
    print("To allow your friends to connect over the internet, Ngrok requires")
    print("a free account token from: https://dashboard.ngrok.com/signup")
    print("")
    token = input("Paste your Ngrok Authtoken here: ").strip()
    if token:
        with open(token_file, "w") as f:
            f.write(token)
        return token
    return None

def main():
    token = get_token()
    if not token:
        print("No authtoken provided. Exiting.")
        return

    print("\n[1/3] Connecting to Daytona Cloud sandbox...")
    client = Daytona(config=DaytonaConfig(api_key=API_KEY))
    s = client.v0.get(SANDBOX_ID)
    print(f"      Sandbox connected: {s.id} (Status: {s.state})")

    print("[2/3] Configuring Ngrok on Daytona...")
    s.process.exec(f"/usr/local/bin/ngrok config add-authtoken {token}")

    print("[3/3] Launching Ngrok TCP tunnel for port 25565...")
    s.process.exec("tmux kill-session -t ngrok 2>/dev/null")
    s.process.exec("tmux new-session -d -s ngrok '/usr/local/bin/ngrok tcp 25565 --log=stdout'")
    
    print("Waiting 4 seconds for tunnel registration...")
    time.sleep(4)

    # Query Ngrok API on Daytona
    res = s.process.exec("curl -s http://127.0.0.1:4040/api/tunnels")
    try:
        data = json.loads(res.result)
        tunnels = data.get("tunnels", [])
        if tunnels:
            public_url = tunnels[0].get("public_url", "")
            # e.g. tcp://0.tcp.ngrok.io:12345
            clean_addr = public_url.replace("tcp://", "")
            print("=" * 65)
            print("       >>> NGROK PUBLIC SERVER ADDRESS FOR FRIENDS <<<")
            print("=" * 65)
            print(f"  Public IP / Address:  {clean_addr}")
            print("")
            print("  Give this address to your friends to enter into Minecraft!")
            print("  Example: Multiplayer -> Direct Connection -> " + clean_addr)
            print("=" * 65)
        else:
            print("Could not find active tunnel in response. Ngrok output:")
            print(res.result)
    except Exception as e:
        print("Error parsing tunnel data:", e)
        print("Raw response:", res.result)

if __name__ == "__main__":
    main()
