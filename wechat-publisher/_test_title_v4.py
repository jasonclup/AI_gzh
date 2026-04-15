"""测试标题系统v5 — 验证3项修复：
1. 关键词提取：品牌名优先（英伟达>突破，金立>创始人）
2. 去重率提升（目标>90%，之前66%）
3. 长度下限保护（≥16字，之前最短14字）
"""
import sys
sys.path.insert(0, '.')
from modules.article_generator import ArticleGenerator

gen = ArticleGenerator({})

topics = [
    '交管部门回应新能源车牌绿色变白色',       # 政策/概念类 → 应出"新能源"
    '英伟达日线十连涨 市值突破4万亿美元',        # 财经+品牌类 → 应出"英伟达"
    '第139届广交会今天正式开展',                 # 新闻类 → 应出"广交会"
    '金立创始人刘立荣消失8年后现身印尼',         # 人物+品牌类 → 应出"金立"
    '苹果发布M5芯片 AI性能提升3倍',             # 科技+品牌类 → 应出"苹果"
]

print('=' * 74)
print('Title System v5  |  5 topics x 5 titles = 25 titles')
print('Fix: brand-first keywords / dedup≥90% / min 16 chars')
print('=' * 74)

all_titles = []
for t in topics:
    print(f'\n[TOPIC] {t}')
    used_for_topic = set()
    for i in range(5):
        title = gen._generate_catchy_title(t, used_titles=used_for_topic)
        used_for_topic.add(title)
        all_titles.append(title)
        clen = len(title)
        blen = len(title.encode('utf-8'))
        status = 'OK' if clen >= 16 else 'SHORT'
        print(f'  {i+1}. [{clen:2d}ch/{blen:2d}B] {status} {title}')

# Dedup test - 更严格的去重测试
print('\n' + '=' * 74)
t_test = topics[0]
used_set = set()
dup_count = 0
total_calls = 20
for i in range(total_calls):
    t = gen._generate_catchy_title(t_test, used_titles=used_set)
    if t in used_set:
        dup_count += 1
    else:
        used_set.add(t)

unique_rate = len(used_set) / total_calls * 100
print(f'[DEDUP TEST] Same topic x {total_calls} calls:')
print(f'  Unique: {len(used_set)}/{total_calls} = {unique_rate:.0f}%% (target >90%%)')

# Length distribution
print('\n[LENGTH STATS]')
lengths = [len(t) for t in all_titles]
b_lengths = [len(t.encode('utf-8')) for t in all_titles]
short_ones = [l for l in lengths if l < 16]
print(f'  Min: {min(lengths)}ch | Max: {max(lengths)}ch | Avg: {sum(lengths)/len(lengths):.1f}ch')
print(f'  <16ch count: {len(short_ones)} (target: 0)')
print(f'  Total templates in pool: {len(gen.CATCHY_TITLE_PATTERNS)}')
