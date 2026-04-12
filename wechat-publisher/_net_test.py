# -*- coding: utf-8 -*-
"""Quick test: verify hot topics fetch works with real network."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}]}
f = HotTopicFetcher(config)
topics = f.fetch_all()

with open('_net_test_result.txt', 'w', encoding='utf-8') as out:
    out.write(f"TOTAL={len(topics)}\n")
    for t in topics[:15]:
        src = t.get('source', '?')
        title = t.get('title', '')[:40]
        hv = t.get('hot_value', 0)
        out.write(f"  [{src}] {title} ({hv})\n")
    out.write("TEST_DONE\n")
print("Script finished")
