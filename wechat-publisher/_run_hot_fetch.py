# -*- coding: utf-8 -*-
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

result = []
print(f'=== 获取到 {len(topics)} 个热点 ===')
for i, t in enumerate(topics[:15], 1):
    src = t.get('source', '?')
    title = t['title']
    hv = t.get('hot_value', 0)
    cat = t.get('category', '')
    url = t.get('url', '')
    print(f'{i:2d}. [{src}] {title} (热度:{hv})')
    result.append({
        'rank': i,
        'source': src,
        'title': title,
        'hot_value': hv,
        'category': cat,
        'url': url
    })

# Save to temp file for next step
with open('_temp_topics.json', 'w', encoding='utf-8') as f:
    json.dump(result[:10], f, ensure_ascii=False, indent=2)

print('\n已保存10个热点到 _temp_topics.json')
