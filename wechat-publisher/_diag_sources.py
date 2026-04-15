# -*- coding: utf-8 -*-
"""快速诊断：3个外部热点源的连通状态"""
import sys, json, time, urllib.request, socket
from datetime import datetime

PROJECT = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher"
sys.path.insert(0, PROJECT)

TIMEOUT = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/json,*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

SOURCES = {
    "今日头条": "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc",
    "百度热搜": "https://top.baidu.com/board?tab=realtime",
    "Tophub微博": "https://tophub.today/n/KqndgxeLl9",
}

results = {}

for name, url in SOURCES.items():
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={**HEADERS, 'Referer': url})
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        data = resp.read()
        elapsed = round((time.time() - start) * 1000)
        enc = 'utf-8'
        for e in ['utf-8', 'gbk']:
            try:
                text = data.decode(e)
                break
            except:
                continue
        
        # 简单判断是否有有效内容
        has_json = text.strip().startswith('{')
        has_titles = len(text) > 500 and ('title=' in text or '<a' in text or 'Title' in text)
        
        results[name] = {
            "ok": True,
            "status": resp.status,
            "size_bytes": len(data),
            "elapsed_ms": elapsed,
            "encoding": enc,
            "has_valid_content": has_json or has_titles,
            "content_type": "json" if has_json else ("html" if has_titles else "unknown"),
        }
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        results[name] = {
            "ok": False,
            "error": str(e)[:120],
            "elapsed_ms": elapsed,
        }

summary = {
    "test_time": datetime.now().isoformat(),
    "timeout_seconds": TIMEOUT,
    "sources": results,
    "all_ok": all(r.get("ok") and r.get("has_valid_content") for r in results.values()),
}

print(json.dumps(summary, ensure_ascii=False, indent=2))
