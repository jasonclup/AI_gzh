# -*- coding: utf-8 -*-
"""最小化测试：用最短标题创建草稿，确认API可用"""
import sys, json
from pathlib import Path
sys.path.insert(0, r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")
import yaml
from modules.wechat_api import WeChatPublisher

cfg = yaml.safe_load(Path("config.yaml").read_text(encoding="utf-8")) or {}
pub = WeChatPublisher(cfg)

# Minimal article
test_articles = [
    {
        "title": "测试",
        "author": "AI",
        "digest": "测试摘要",
        "content": "<p>这是一段测试内容。</p>",
        "thumb_media_id": "",
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
]

token = pub._get_access_token()
print(f"Token OK: {token[:15]}...")

import requests
url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
payload = {"articles": test_articles}

print(f"Sending title: [{test_articles[0]['title']}] ({len(test_articles[0]['title'].encode('utf-8'))} bytes)")

resp = requests.post(url, json=payload, timeout=30)
data = resp.json()

print(f"Response: {json.dumps(data, ensure_ascii=False)}")

if data.get("media_id"):
    print(f"\nOK DRAFT CREATED! media_id={data['media_id']}")
else:
    print(f"\nFAILED: errcode={data.get('errcode')} errmsg={data.get('errmsg')}")
    
    # Try even simpler
    print("\n--- Try 2: single char title ---")
    test_articles[0]["title"] = "好"
    resp2 = requests.post(url, json={"articles": test_articles}, timeout=30)
    data2 = resp2.json()
    print(f"Response2: {json.dumps(data2, ensure_ascii=False)}")
    if data2.get("media_id"):
        print(f"\nOK DRAFT CREATED (try 2)! media_id={data2['media_id']}")
    else:
        print(f"\nFAILED(try 2): errcode={data2.get('errcode')} errmsg={data2.get('errmsg')}")
