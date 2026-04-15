"""快速测试：热点+文章（无配图）"""
import sys
sys.path.insert(0, '.')
from modules.hot_topics import HotTopicFetcher
from modules.article_generator import ArticleGenerator
import json

# Step 1: 热点
fetcher = HotTopicFetcher({})
topics = fetcher.fetch_all()
if not topics:
    print('[FAIL] No topics')
    sys.exit(1)

t = topics[0].get('title', topics[0].get('name', str(topics[0])))
print(f'[HOT] {t}')

# Step 2: 文章
gen = ArticleGenerator({})
article = gen.generate(topic=t, title='')
print(f'[TITLE] {article["title"]}')
print(f'[SECTIONS] {len(article.get("sections", []))}')

with open('output/_pipeline_step2_result.json', 'w', encoding='utf-8') as f:
    json.dump(article, f, ensure_ascii=False, indent=2)
print('[OK] Saved')
