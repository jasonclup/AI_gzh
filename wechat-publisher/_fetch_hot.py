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

result = []
for t in topics[:15]:
    result.append({
        'title': t.get('title', ''),
        'hot_value': t.get('hot_value', 0),
        'source': t.get('source', ''),
        'url': t.get('url', '')
    })

print(json.dumps({'total': len(result), 'topics': result}, ensure_ascii=False, indent=2))
