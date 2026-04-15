# -*- coding: utf-8 -*-
"""抓取热点话题"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()[:10]

output = []
for i, t in enumerate(topics, 1):
    output.append({
        'rank': i,
        'title': t['title'],
        'hot_value': t.get('hot_value', 0),
        'source': t.get('source', ''),
    })

print(json.dumps(output, ensure_ascii=False, indent=2))
