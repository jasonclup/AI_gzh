# -*- coding: utf-8 -*-
"""Isolate: is it title length or content that causes 45003?"""
import sys, json
from pathlib import Path
sys.path.insert(0, r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")
import yaml, requests

cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {}
r1 = requests.get("https://api.weixin.qq.com/cgi-bin/token", params={
    "grant_type": "client_credential", "appid": cfg["WECHAT_APPID"], "secret": cfg["WECHAT_SECRET"]}, timeout=15)
token = r1.json()["access_token"]
url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"

# Get real thumb
r2 = requests.post(f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}",
    json={"type": "image", "offset": 0, "count": 1}, timeout=15)
tid = r2.json()["item"][0]["media_id"]

def test(label, title, content):
    body = {"articles": [{"title": title, "author": "AI", "digest": "摘要测试",
        "content": content, "thumb_media_id": tid, "need_open_comment": 1, "only_fans_can_comment": 0}]}
    r = requests.post(url, json=body, timeout=30)
    d = r.json()
    ok = bool(d.get("media_id"))
    tbytes = len(title.encode('utf-8'))
    cbytes = len(content.encode('utf-8'))
    print(f"{label}: {'OK' if ok else 'FAIL'} errcode={d.get('errcode','')} | title={tbytes}B content={cbytes}B")
    if d.get("media_id"):
        print(f"  -> DRAFT ID: {d['media_id']}")
    return ok

# Test series
print("=== Isolating 45003 root cause ===")

test("A: short all", "测试", "<p>Hi</p>")
test("B: long title + short content", safe_title := "苹果提醒用户更新iOS以免受网页攻击", "<p>Hi</p>")
test("C: short title + long content", "测试", "<p>" + "内容"*200 + "</p>")
test("D: long title + long html", safe_title,
     '<section style="font-size:16px"><p>这是正文内容，关于苹果提醒用户更新iOS以免受网页攻击的深度分析。作为一个长期关注该领域的人，今天我想从几个角度客观梳理一下这件事的来龙去脉。</p></section>'
     * 6)

# Try exact same as working case but longer title
test("E: like success case but longer title", "苹果提醒用户更新iOS安全漏洞请尽快升级系统版本", "<p>正文内容</p>")
