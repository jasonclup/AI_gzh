# -*- coding: utf-8 -*-
import sys
import json
sys.path.insert(0, '.')
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

print(f'\n=== Hot Topics ({len(topics)} total) ===')
for i, t in enumerate(topics[:15], 1):
    src = t.get('source', '?')
    hv = t.get('hot_value', 0)
    title = t.get('title', '')
    print(f'{i:2d}. [{src}] {title} (hot:{hv})')

print('\n---JSON_OUTPUT---')
print(json.dumps(topics[:10], ensure_ascii=False, indent=2))
