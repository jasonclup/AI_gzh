# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, os.path.dirname(__file__))
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}, {'name': 'Tophub微博', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

print(f'Total topics: {len(topics)}')
for i, t in enumerate(topics[:15], 1):
    src = t.get('source', '?')
    hv = t.get('hot_value', 0)
    title = t.get('title', '')
    print(f'{i:2d}. [{src}] {title} (hot:{hv})')

print('---JSON_START---')
print(json.dumps(topics[:15], ensure_ascii=False, indent=2))
print('---JSON_END---')
