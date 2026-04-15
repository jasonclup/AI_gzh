# -*- coding: utf-8 -*-
import sys, yaml
sys.path.insert(0, r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")
from modules.hot_topics import HotTopicFetcher

cfg = yaml.safe_load(open("config.yaml", "r", encoding="utf-8")) or {}
print(f"Config HOT_SOURCES: {cfg.get('HOT_SOURCES', [])}")
f = HotTopicFetcher(cfg)

# Test individual sources
print("\n--- Testing each source ---")
for name, fn in [('今日头条', f._fetch_toutiao), ('百度热搜', f._fetch_baidu)]:
    try:
        items = fn()
        print(f"{name}: {len(items)} items")
        if items:
            print(f"   First: {items[0].get('title','')}")
    except Exception as e:
        print(f"{name}: ERROR - {e}")

# Test fetch_all
print("\n--- fetch_all result ---")
topics = f.fetch_all()
print(f"Total: {len(topics)}")
for i, t in enumerate(topics[:5], 1):
    src = t.get("source", "?")
    ttl = t.get("title", "")
    hv = t.get("hot_value", 0)
    print(f"  [{i}] source={src} | hot={hv} | {ttl}")
if topics:
    print(f"\nFirst topic SOURCE: {topics[0].get('source')}")
