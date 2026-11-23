import urllib.request
import json

official_slugs = [
    'fresh-animations',
    'fresh-animations-extensions',
    'fa-player-extension',
    'fresh-animations-details',
    'fresh-animations-objects',
    'fresh-animations-emissive',
    'fresh-animations-spiders',
    'fresh-animations-creepers',
    'fresh-animations-quivers'
]

def check_versions():
    for slug in official_slugs:
        url = f'https://api.modrinth.com/v2/project/{slug}/version'
        req = urllib.request.Request(url, headers={'User-Agent': 'SDCraft/1.0'})
        try:
            with urllib.request.urlopen(req) as resp:
                versions = json.loads(resp.read().decode('utf-8'))
                if not versions:
                    print(f"[{slug}] No versions found")
                    continue
                # Pick best version
                best_v = None
                for v in versions:
                    gv = v.get('game_versions', [])
                    if '26.3' in gv or '26.2' in gv or '26.1' in gv:
                        best_v = v
                        break
                if not best_v:
                    best_v = versions[0]
                
                print(f"=== {slug} ===")
                print(f"  Version: {best_v.get('name')}")
                print(f"  Game versions: {best_v.get('game_versions')[:4]}")
                for f in best_v.get('files', []):
                    if f.get('primary', False) or len(best_v.get('files')) == 1:
                        print(f"  File: {f.get('filename')} | Size: {f.get('size')} | URL: {f.get('url')}")
        except Exception as e:
            print(f"[{slug}] Error: {e}")

if __name__ == '__main__':
    check_versions()
