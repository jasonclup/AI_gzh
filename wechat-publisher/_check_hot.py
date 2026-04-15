# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, '.')
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

print(f'Total topics: {len(topics)}')
for i, t in enumerate(topics[:10]):
    src = t.get('source', '?')
    title = t.get('title', '')
    hv = t.get('hot_value', 0)
    print(f'{i+1}. [{src}] {title} ({hv})')

print(f'Source: {topics[0].get("source", "?") if topics else "NONE"}')
