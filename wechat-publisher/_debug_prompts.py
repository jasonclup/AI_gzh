# -*- coding: utf-8 -*-
"""Debug: 验证最终prompt差异"""
import sys, os, yaml
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher")

from modules.hot_topics import HotTopicFetcher
from modules.article_generator import ArticleGenerator
from modules.image_generator import ImageGenModule
from tools.image_helper import _build_ai_prompt, _get_cache_key

with open(r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\config.yaml", 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 抓热点+生成文章
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()
topic_text = topics[0].get('title', str(topics[0])) if isinstance(topics[0], dict) else str(topics[0])

article_gen = ArticleGenerator(config)
article = article_gen.generate(topic=topic_text, title=topic_text)

img_gen = ImageGenModule(config)

print("=" * 70)
print(" DEBUG: 检查每张图的实际最终prompt和cache key")
print("=" * 70)

# 封面
cover_prompt = img_gen._build_semantic_prompt(topic_text, article['title'], 
    hint=article['title'], para_text=article['title'], is_cover=True)
cover_final = _build_ai_prompt(cover_prompt)
cover_key = _get_cache_key(cover_final, "900x506")
print(f"\n[COVER] semantic: {cover_prompt[:100]}")
print(f"         ai_final: {cover_final[:200]}")
print(f"         cache_key: {cover_key}")

# 各段落
for p in article.get('paragraphs', []):
    if not p.get('needs_image'):
        continue
    
    # Step 1: _build_semantic_prompt
    sem_prompt = img_gen._build_semantic_prompt(
        topic_text, title=article['title'],
        hint=p.get('image_hint',''), para_text=p['text'][:140]
    )
    
    # Step 2: _build_ai_prompt (这是实际发给API的)
    ai_final = _build_ai_prompt(sem_prompt)
    
    # Cache key
    cache_key = _get_cache_key(ai_final, "1080x1920")
    
    print(f"\n[PARA {p['index']+1}]")
    print(f"  image_hint: {p.get('image_hint','')[:80]}...")
    print(f"  semantic_prompt: {sem_prompt[:120]}...")
    print(f"  >>> FINAL AI PROMPT: {ai_final[:250]}...")
    print(f"  >>> CACHE KEY: {cache_key}")
    print(f"  >>> prompt length: {len(ai_final)} chars")
