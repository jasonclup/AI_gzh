# -*- coding: utf-8 -*-
"""Direct API test for draft creation - bypass all wrappers"""
import sys, json
from pathlib import Path
sys.path.insert(0, r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")
import yaml, requests

cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {}
appid = cfg["WECHAT_APPID"]
secret = cfg["WECHAT_SECRET"]

# Get token
r1 = requests.get("https://api.weixin.qq.com/cgi-bin/token", params={
    "grant_type": "client_credential", "appid": appid, "secret": secret}, timeout=15)
token = r1.json()["access_token"]
print(f"Token: {token[:15]}...")

url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

# Test 1: absolute minimum
print("\n=== Test 1: min ===")
body = {"articles": [{"title": "T", "content": "<p>Hi</p>", "thumb_media_id": "0"}]}
r = requests.post(url, json=body, timeout=15)
d = r.json()
print(f"Result: {json.dumps(d, ensure_ascii=False)}")

# Test 2: Chinese short title
print("\n=== Test 2: zh short ===")
body["articles"][0]["title"] = "测试"
r2 = requests.post(url, json=body, timeout=15)
d2 = r2.json()
print(f"Result: {json.dumps(d2, ensure_ascii=False)}")

# Test 3: use real thumb_id from materials
print("\n=== Test 3: real thumb ===")
r3 = requests.post(f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}",
    json={"type": "image", "offset": 0, "count": 3}, timeout=15)
mats = r3.json().get("item", [])
if mats:
    tid = mats[0]["media_id"]
    body["articles"][0] = {
        "title": "苹果提醒更新iOS",
        "author": "AI",
        "digest": "摘要",
        "content": "<p>正文内容测试</p>",
        "thumb_media_id": tid,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    r4 = requests.post(url, json=body, timeout=15)
    d4 = r4.json()
    print(f"Result: {json.dumps(d4, ensure_ascii=False)}")
    if d4.get("media_id"):
        print(f"\n*** SUCCESS! Draft media_id={d4['media_id']} ***")
