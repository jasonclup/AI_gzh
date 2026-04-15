"""Test if different prompts produce different images"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import urllib.request, json, hashlib

prompts = [
    "GPT-5即将发布，AI技术再次突破，科技感封面",
    "OpenAI发布最新大模型，算力提升百倍，数据中心服务器",
    "人工智能改变生活场景，智能家居设备互联",
    "未来科技城市天际线，霓虹灯与数字网络",
]

url = "https://image.pollinations.ai/prompt"
results = []

for i, prompt in enumerate(prompts):
    payload = json.dumps({
        "prompt": prompt,
        "width": 1280,
        "height": 720,
        "nologo": True,
        "model": "flux",
        "seed": (hash(prompt) % 10000)
    }).encode('utf-8')

    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0')

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            md5 = hashlib.md5(data).hexdigest()[:12]
            out = f"_test_img{i}.png"
            with open(out, 'wb') as f:
                f.write(data)
            results.append((out, len(data), md5))
            print(f"[{i}] {len(data)}B MD5={md5} -> {out}")
    except Exception as e:
        print(f"[{i}] ERROR: {e}")

# Check uniqueness
md5s = set(r[2] for r in results)
print(f"\nUnique MD5s: {len(md5s)} / {len(results)}")
if len(md5s) < len(results):
    print("WARNING: Some images are IDENTICAL!")
else:
    print("OK: All images are DIFFERENT!")
