import subprocess, time, sys

print("=" * 65)
print("     SDCRAFT - PLAYIT.GG FREE MINECRAFT TUNNEL LAUNCHER")
print("=" * 65)
print("Starting Playit tunnel (No credit card, 100% free)...")
print("")

cmd = [r"d:\Games\SDCRAFT\tools\playit\playit.exe", "start"]
try:
    p = subprocess.Popen(cmd)
    p.wait()
except KeyboardInterrupt:
    print("\nTunnel stopped.")
