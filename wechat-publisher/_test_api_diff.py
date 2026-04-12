# -*- coding: utf-8 -*-
"""Debug: 直接测试Pollinations对不同prompt是否返回不同图片"""
import sys, os, json, urllib.request, time, hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OUTPUT_DIR = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\output\images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_post(prompt, filename, width=900, height=506):
    """直接用POST请求一张图"""
    url = "https://image.pollinations.ai/prompt"
    payload = json.dumps({
        "prompt": prompt,
        "width": width,
        "height": height,
        "nologo": True,
        "model": "turbo",
        "seed": int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)  # 基于prompt的seed
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = resp.read()
            elapsed = time.time() - t0
        
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, 'wb') as f:
            f.write(data)
        
        sz = len(data)
        md5 = hashlib.md5(data).hexdigest()[:12]
        print(f"  OK {filename}: {sz}B ({sz//1024}KB) md5={md5} time={elapsed:.1f}s")
        return path, sz, md5
    except Exception as e:
        print(f"  FAIL {filename}: {e}")
        return None, 0, None

print("=" * 60)
print(" Testing: 4 completely different prompts")
print("=" * 60)

prompts = [
    "A red apple on a wooden table, photorealistic",
    "Blue ocean waves crashing on rocks at sunset",
    "A cute orange cat sleeping on a white sofa",
    "Futuristic Tokyo city skyline at night with neon lights",
]

results = []
for i, p in enumerate(prompts):
    print(f"\n[{i+1}] Prompt: {p[:60]}...")
    path, sz, md5 = download_post(p, f"test_diff_{i}.png")
    results.append((p, path, sz, md5))
    time.sleep(1)  # 避免限流

print("\n" + "=" * 60)
print(" RESULTS:")
print("=" * 60)
sizes = [r[2] for r in results]
md5s = [r[3] for r in results]
unique_sizes = len(set(sizes))
unique_md5s = len(set(md5s))

for i, (p, path, sz, md5) in enumerate(results):
    print(f"  [{i+1}] {sz//1024}KB | md5={md5} | {p[:40]}...")

print(f"\n  Unique sizes: {unique_sizes}/4")
print(f"  Unique MD5s:  {unique_md5s}/4")

if unique_md5s == 4:
    print("  => PASS: All images are different!")
else:
    print("  => FAIL: Some images are IDENTICAL!")
