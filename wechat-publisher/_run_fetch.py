# -*- coding: utf-8 -*-
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [
    {'name': '今日头条', 'enabled': True},
    {'name': '百度热搜', 'enabled': True},
    {'name': 'Tophub微博', 'enabled': True}
]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

print(f"=== 获取到 {len(topics)} 个热点 ===")
for i, t in enumerate(topics[:15], 1):
    title = t['title']
    hv = t.get('hot_value', 0)
    src = t.get('source', '?')
    print(f"{i:2d}. {title} (热度:{hv} | 来源:{src})")

# Output top 10 as JSON
output = [{'title': t['title'], 'hot_value': t.get('hot_value', 0), 'source': t.get('source', '?'), 'category': t.get('category', '')} for t in topics[:10]]
print('\n===JSON_OUTPUT===')
print(json.dumps(output, ensure_ascii=False, indent=2))
