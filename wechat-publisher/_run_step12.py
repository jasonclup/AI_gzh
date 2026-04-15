# -*- coding: utf-8 -*-
"""流水线 Step 1+2: 热点抓取 + 文章生成（不包含图）
用法: python _run_step12.py [topic_index]
  topic_index: 热点列表中的索引，默认=0（第1条热点）
"""

import sys, os, json, yaml
sys.path.insert(0, os.path.dirname(__file__))

# 从命令行参数读取热点索引
idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0

# 加载配置
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Step 1: 热点抓取
print('=== Step 1: 热点抓取 ===')
from modules.hot_topics import HotTopicFetcher
hot = HotTopicFetcher(config)
topics = hot.fetch_all()
if not topics:
    print('ERROR: 热点为空!')
    sys.exit(1)

if idx >= len(topics):
    print(f'ERROR: 索引{idx}超出范围(共{len(topics)}条)')
    sys.exit(1)

selected = topics[idx]
topic = selected.get('title') if isinstance(selected, dict) else str(selected)
print(f'选题#{idx}: {topic}')

# Step 2: 文章生成
print('\n=== Step 2: 文章生成 ===')
from modules.article_generator import ArticleGenerator
art_gen = ArticleGenerator(config)
article = art_gen.generate(topic, topic)
print(f'标题: {article["title"]}')
print(f'段落数: {len(article.get("paragraphs", []))}')

# 输出结果
out_path = os.path.join(os.path.dirname(__file__), '_pipeline_step2_result.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(article, f, ensure_ascii=False, indent=2)
print(f'\n文章已保存到 {out_path}')
