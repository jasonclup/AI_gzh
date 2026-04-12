# -*- coding: utf-8 -*-
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}, {'name': 'Tophub微博', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

print(f"Total topics fetched: {len(topics)}")
for i, t in enumerate(topics[:15], 1):
    print(f'{i:2d}. {t["title"]} (hot:{t.get("hot_value",0)} src:{t.get("source","?")})')
