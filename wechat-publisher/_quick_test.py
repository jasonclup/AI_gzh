"""Quick test: does fallback return data? Runs in < 3 seconds."""
import sys, os, logging
sys.path.insert(0, os.path.dirname(__file__))
logging.disable(logging.CRITICAL)

from modules.hot_topics import HotTopicFetcher

f = HotTopicFetcher({'HOT_SOURCES': [{'name': 'weibo', 'enabled': True}, {'name': 'baidu', 'enabled': True}]})
topics = f.fetch_all()

print(f"COUNT={len(topics)}")
if topics:
    print(f"SOURCE={topics[0].get('source','NONE')}")
    print(f"FIRST={topics[0]['title'][:30]}")
    print("OK")
else:
    print("FAIL: no topics returned")
