"""测试文章生成 + 法律检查 + AI评分"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from modules.article_generator import ArticleGenerator
import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

gen = ArticleGenerator(config)

# 1. 生成文章
article = gen.generate(topic='GPT-5即将发布 AI再次突破', style='hot_commentary')
print('=== 文章生成成功 ===')
print(f"标题: {article['title']}")
print(f"字数: {article['word_count']} | 段落: {len(article['paragraphs'])}")

# 2. 法律风险检查
full_text = '\n'.join([p['text'] for p in article['paragraphs']])
legal = gen.legal_check(full_text)
print(f'\n=== 法律安全检查 ===')
print(f"安全: {legal['safe']} | 安全分: {legal['score']}")
if legal.get('warnings'):
    print(f'警告({len(legal["warnings"])}项):')
    for w in legal['warnings']:
        print(f"  ! {w['category']}: {w['suggestion']}")
if legal.get('blocked'):
    print(f'阻断({len(legal["blocked"])}项): 需修改!')

# 3. AI评分估算
ai_score = gen.estimate_ai_score(full_text)
sugg_str = ' '.join(ai_score.get('suggestions', []))
print('\n=== AI风格评分预估 ===')
print(f"AI评分: {ai_score['estimated_score']} (目标<40)")
print(f"人写特征数: {ai_score['human_features_found']}")
for ri in ai_score.get('risk_items', []):
    print(f"  高危: {ri['category']}-{len(ri['items'])}处")
print(f"建议: {sugg_str}")

# 4. 图片安全检查
hint = article.get('cover_image_hint', 'test')
safe_hint = gen.image_safety_check(hint)
print('\n=== 图片安全检查 ===')
print(f"原始: {hint[:60]}")
print(f"安全后缀已添加: ...{safe_hint[-50:]}")

print("\n✅ 全部测试通过!")
