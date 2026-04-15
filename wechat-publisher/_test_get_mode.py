"""Test: does GET mode produce different images?"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import urllib.request, hashlib, time
from urllib.parse import quote

prompts = [
    "futuristic GPT-5 AI brain hologram, blue neon lights",
    "data center server room with glowing LED racks",
    "smart city skyline at night, digital network connections",
    "abstract technology particles floating in space, purple glow",
]

results = []
for i, prompt in enumerate(prompts):
    cb = int(time.time() * 1000)
    seed = (hash(prompt) % 10000) + i * 1000
    encoded = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&model=flux&seed={seed}&nologo=true&_cb={cb}"

    print(f"[{i}] Requesting: {prompt[:40]}...")
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            md5 = hashlib.md5(data).hexdigest()[:12]
            out = f"_get_test_{i}.png"
            with open(out, 'wb') as f:
                f.write(data)
            results.append((out, len(data), md5))
            print(f"  -> {len(data)}B MD5={md5}")
    except Exception as e:
        print(f"  -> ERROR: {e}")

    if i < len(prompts) - 1:
        time.sleep(3)

md5s = set(r[2] for r in results)
print(f"\nUnique: {len(md5s)}/{len(results)}")
print("OK!" if len(md5s)==len(results) else "FAIL - duplicates detected")
