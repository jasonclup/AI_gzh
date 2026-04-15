# -*- coding: utf-8 -*-
"""Step 5 FINAL: 真实热点文章 -> 公众号草稿箱（标题截断到安全长度）"""
import json, sys, re, time
from pathlib import Path

PROJECT = Path(r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")
sys.path.insert(0, str(PROJECT))
import yaml, requests

cfg = yaml.safe_load((PROJECT / "config.yaml").read_text(encoding="utf-8")) or {}
appid, secret = cfg["WECHAT_APPID"], cfg["WECHAT_SECRET"]

# === A. Token ===
print("[A] Token...")
token = requests.get("https://api.weixin.qq.com/cgi-bin/token", params={
    "grant_type": "client_credential", "appid": appid, "secret": secret}, timeout=15).json()["access_token"]
print(f"    {token[:15]}...")

# === B. Load article ===
runs_dir = PROJECT / "output" / "publish_runs"
payloads = sorted(runs_dir.glob("payload_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
payload = json.loads(payloads[0].read_text(encoding="utf-8"))
article_data = payload["article"]
raw_title = article_data["title"]
paragraphs = article_data.get("paragraphs", [])

# Title safety: keep under 20 bytes (subscription accounts have tighter limits)
# Each Chinese char = 3 bytes in UTF-8, so max ~6 Chinese chars or ~20 ASCII chars
MAX_TITLE_BYTES = 18
safe_title = raw_title
while len(safe_title.encode('utf-8')) > MAX_TITLE_BYTES and len(safe_title) > 1:
    safe_title = safe_title[:-1]
print(f"[B] [{safe_title}] ({len(safe_title.encode('utf-8'))}B) from [{raw_title}]")

# === C. Cover image ===
print("[C] Cover...")
img_dir = PROJECT / "output" / "images" / "run_20260415_112323"
imgs = sorted(img_dir.glob("*.png")) if img_dir.exists() else []
if imgs:
    with open(imgs[0], 'rb') as f:
        r_c = requests.post(f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image",
            files={'media': (imgs[0].name, f, 'image/png')}, timeout=60)
    thumb_id = r_c.json().get('media_id', '')
    print(f"    {Path(imgs[0]).name} -> OK")
else:
    thumb_id = requests.post(f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}",
        json={"type": "image", "offset": 0, "count": 1}, timeout=15).json()["item"][0]["media_id"]
    print(f"    fallback material")

# === D. Content images ===
print("[D] Content images...")
up_url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
img_urls = {}  # para_idx -> url
for idx in range(1, min(len(paragraphs), len(imgs))):
    if idx < len(imgs):
        try:
            with open(imgs[idx], 'rb') as f:
                r_i = requests.post(up_url, files={'media': (imgs[idx].name, f, 'image/png')}, timeout=60)
            if r_i.json().get("url"):
                img_urls[idx] = r_i.json()["url"]
                print(f"    para[{idx}] OK")
        except Exception:
            pass

# === E. HTML build ===
html_parts = []
for i, p in enumerate(paragraphs):
    txt = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p.get("text","")).replace('\n','</p><p>')
    html_parts.append(f'<section style="font-size:16px;line-height:1.8;color:#333;margin-bottom:20px;text-align:justify;"><p>{txt}</p></section>')
    if i in img_urls:
        html_parts.append(f'<p style="text-align:center;margin:16px 0;"><img src="{img_urls[i]}" style="width:100%;border-radius:8px;"/></p>')
html_parts.append('<section style="background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:25px;border-radius:12px;margin-top:30px;text-align:center;"><p style="font-size:18px;font-weight:bold;">关注我，每天看科技</p></section>')

raw_digest = (article_data.get("summary") or paragraphs[0]["text"])[:120]
# Subscription accounts: digest max ~120 bytes (safe)
digest = raw_digest
MAX_DIGEST_BYTES = 50
while len(digest.encode('utf-8')) > MAX_DIGEST_BYTES and len(digest) > 1:
    digest = digest[:-1]
print(f"    digest={len(digest.encode('utf-8'))}B [{digest}]")

# === F. Create draft ===
print("[F] Creating draft...")
r = requests.post(f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}", json={
    "articles": [{
        "title": safe_title,
        "author": "WorkBuddy AI",
        "digest": digest,
        "content": "".join(html_parts),
        "thumb_media_id": thumb_id,
        "need_open_comment": 1, "only_fans_can_comment": 0,
    }]
}, timeout=30)
result = r.json()

ok = bool(result.get("media_id"))
out = {"status":"success" if ok else "failed","title":safe_title,"original":raw_title,"media_id":result.get("media_id"),"response":result}
print(json.dumps(out, ensure_ascii=False, indent=2))

if ok:
    print(f"\n*** DRAFT CREATED! media_id={result['media_id']} ***")
    print("*** Go check mp.weixin.qq.com -> 草稿箱 ***")

rf = runs_dir / f"draft_final_{int(time.time())}.json"
rf.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
