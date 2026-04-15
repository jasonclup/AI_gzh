"""Quick test: can we reach Pollinations.ai?"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import urllib.request, json

url = "https://image.pollinations.ai/prompt"
prompt = "futuristic AI technology scene, glowing digital network, blue neon lights, no people"
payload = json.dumps({
    "prompt": prompt,
    "width": 1280,
    "height": 720,
    "nologo": True,
    "model": "flux",
    "seed": 42
}).encode('utf-8')

req = urllib.request.Request(url, data=payload, method='POST')
req.add_header('Content-Type', 'application/json')
req.add_header('User-Agent', 'Mozilla/5.0')

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        print(f"Status: {resp.status}")
        print(f"Size: {len(data)} bytes ({len(data)//1024}KB)")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        # Save to file
        out = "_test_poll_img.png"
        with open(out, 'wb') as f:
            f.write(data)
        print(f"Saved: {out}")
except Exception as e:
    print(f"ERROR: {e}")
