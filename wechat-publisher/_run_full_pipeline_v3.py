# -*- coding: utf-8 -*-
"""
完整内容生产流水线 v3 — 三大增长引擎集成版
=================================================
流程（8步）:
  1. 热点抓取          ← hot_topics.py
  2. 选题评分排序      ← ★ topic_scorer.py (NEW)
  3. 竞品洞察参考      ← ★ competitor_monitor.py (NEW)
  4. 文章撰写          ← article_generator.py (Agent LLM真人写作)
  5. 文章数据记录      ← ★ article_performance.py (NEW)
  6. AI配图生成        ← image_generator.py
  7. HTML渲染 + 预览
  8. Playwright截图    (可选)

对比v2的变化:
  - Step 1后新增: 选题评分器(从N个热点选最优话题)
  - Step 2前新增: 竞品监控(头部账号是否已写、学什么角度)
  - Step 2后新增: 数据回流(记录文章元数据供后续表现分析)
"""

import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import yaml
config_path = PROJECT_ROOT / 'config.yaml'
CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8')) if config_path.exists() else {}

os.chdir(PROJECT_ROOT)


def build_html(title, paragraphs, cover_path=None):
    """构建移动端适配HTML文章页面"""
    def to_rel(p):
        if not p:
            return ''
        pp = Path(p).resolve()
        try:
            rel = pp.relative_to(PROJECT_ROOT.resolve())
            parts = list(rel.parts)
            if len(parts) >= 2 and parts[0] == 'output' and parts[1] == 'images':
                return '../images/' + '/'.join(parts[2:])
            return f"/{'/'.join(parts)}"
        except ValueError:
            return str(pp)

    cover_url = to_rel(cover_path) if cover_path else ''
    cover_html = f'<img src="{cover_url}" class="cover-img" alt="封面">' if cover_url else ''

    para_htmls = []
    for idx, p in enumerate(paragraphs):
        txt = p.get('text', '').strip()
        if not txt:
            continue
        ptype = p.get('type', 'body')
        css = 'para-opening' if ptype == 'opening' else ('para-closing' if ptype == 'closing' else 'para-body')

        img_html = ''
        img_path = p.get('image_path')
        if img_path and os.path.exists(str(img_path)):
            img_url = to_rel(img_path)
            hint_html = f'<p class="img-caption">{p.get("image_hint", "")}</p>' if p.get('image_hint') else ''
            img_html = f'<div class="para-img-wrap"><img src="{img_url}" class="para-img" alt="配图">{hint_html}</div>'

        para_htmls.append(f'''
<div class="paragraph {css}">
  <div class="para-text">{txt}</div>
  {img_html}
</div>''')

    paragraphs_block = '\n'.join(para_htmls)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">
<title>{title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB",sans-serif;
  background:#fff; color:#333; line-height:1.8; font-size:17px;
  padding:12px; max-width:100vw;
}}
.cover-img {{ width:100%; border-radius:10px; margin-bottom:20px; box-shadow:0 4px 16px rgba(0,0,0,.15); }}
h1 {{ font-size:24px; font-weight:800; line-height:1.4; margin-bottom:18px; }}
.paragraph {{ margin-bottom:22px; }}
.para-opening .para-text {{ font-size:19px; font-weight:700; color:#111; }}
.para-body .para-text {{ font-size:17px; text-indent:2em; }}
.para-closing .para-text {{ font-size:17px; font-style:italic; color:#555; }}
.para-img-wrap {{ margin:14px 0; text-align:center; }}
.para-img {{ max-width:100%; border-radius:8px; box-shadow:0 3px 12px rgba(0,0,0,.12); }}
.img-caption {{ font-size:13px; color:#999; font-style:italic; margin-top:6px; }}
</style>
</head>
<body>
{cover_html}
<h1>{title}</h1>
{paragraphs_block}
</body>
</html>'''


# ============================================================
# Step 1/8: 热点抓取
# ============================================================
print("\n" + "="*60)
print("Step 1/8: 热点抓取")
print("="*60)

from modules.hot_topics import HotTopicFetcher
fetcher = HotTopicFetcher(CONFIG)
raw_topics = fetcher.fetch_all()
print(f"  [OK] 抓取到 {len(raw_topics)} 条热点")

step1_result = {
    'status': 'ok',
    'total': len(raw_topics),
    'top5': [
        {'title': t.get('title', str(t))[:60] if isinstance(t, dict) else str(t)[:60],
         'heat': t.get('heat', '?') if isinstance(t, dict) else '?'}
        for t in raw_topics[:5]
    ]
}

for t in raw_topics[:5]:
    label = "  -"
    if isinstance(t, dict):
        print(f"{label} [{t.get('heat','?')}] {t.get('title','')[:60]}")
    else:
        print(f"{label} {str(t)[:60]}")


# ============================================================
# Step 2/8: 选题评分 ★ 新增模块
# ============================================================
print("\n" + "="*60)
print("Step 2/8: 选题评分排序 (topic_scorer)")
print("="*60)

from modules.topic_scorer import TopicScorer

scorer = TopicScorer(CONFIG)
scored_topics = scorer.score_topics_batch(raw_topics)

# 按分数降序排列
scored_topics.sort(key=lambda x: x.get('final_score', 0), reverse=True)

print(f"\n  [OK] 全部 {len(scored_topics)} 个热点已评分:\n")
for i, st in enumerate(scored_topics[:10]):
    grade = st.get('grade', '?')
    score = st.get('final_score', 0)
    title_text = st.get('original_title', st.get('title', ''))[:55]
    detail = st.get('score_detail', {})
    highlights = []
    if detail.get('heat_score', 0) >= 20: highlights.append(f"热度{detail['heat_score']}")
    if detail.get('controversy_score', 0) >= 14: highlights.append(f"争议{detail['controversy_score']}")
    if detail.get('niche_match_score', 0) >= 16: highlights.append(f"赛道{detail['niche_match_score']}")
    hl_str = f" ({', '.join(highlights)})" if highlights else ""
    print(f"  #{i+1:>2} [{grade}] {score:>3}分 | {title_text}{hl_str}")

# 统计各等级数量
grade_counts = {}
for st in scored_topics:
    g = st.get('grade', '?')
    grade_counts[g] = grade_counts.get(g, 0) + 1

print(f"\n  等级分布: ", end="")
for g in ['S', 'A', 'B', 'C', 'D']:
    c = grade_counts.get(g, 0)
    if c > 0:
        print(f"{g}={c}  ", end="")
print()

# 选最优话题：优先A级以上，否则取最高分
best_topic_data = None
for st in scored_topics:
    if st.get('grade') in ('S', 'A'):
        best_topic_data = st
        break
if not best_topic_data and scored_topics:
    best_topic_data = scored_topics[0]

selected_topic_title = best_topic_data.get('original_title',
                            best_topic_data.get('title', '')) if best_topic_data else ''
selected_topic_score = best_topic_data.get('final_score', 0) if best_topic_data else 0
selected_topic_grade = best_topic_data.get('grade', '?') if best_topic_data else '?'

print(f"\n  >> 选定话题: 【{selected_topic_grade}级 | {selected_topic_score}分】{selected_topic_title}")

step2_result = {
    'status': 'ok',
    'scored_count': len(scored_topics),
    'grade_distribution': grade_counts,
    'selected': {
        'title': selected_topic_title,
        'score': selected_topic_score,
        'grade': selected_topic_grade,
        'score_detail': best_topic_data.get('score_detail', {}) if best_topic_data else {}
    }
}


# ============================================================
# Step 3/8: 竞品洞察 ★ 新增模块
# ============================================================
print("\n" + "="*60)
print("Step 3/8: 竞品洞察参考 (competitor_monitor)")
print("="*60)

from modules.competitor_monitor import CompetitorMonitor

monitor = CompetitorMonitor()

# 快速检查：这个话题竞品有没有写过？有什么角度可以参考？
insights = monitor.quick_check(selected_topic_title)

print(f"\n  话题: {selected_topic_title}")
print(f"  竞品覆盖度: {insights.get('coverage_level', 'unknown')}")

if insights.get('covered_by'):
    print(f"\n  已被以下账号覆盖:")
    for acc in insights['covered_by'][:5]:
        print(f"    - {acc.get('account_name', '?')}: {acc.get('article_title', '')[:50]}")
else:
    print("\n  该话题暂未被监控账号覆盖 -> 写作空间大!")

if insights.get('suggested_angles'):
    print(f"\n  建议写作角度:")
    for angle in insights['suggested_angles'][:5]:
        print(f"    * {angle.get('angle', '')} (来源: {angle.get('source_account', '系统建议')})")

if insights.get('writing_tips'):
    tips = insights['writing_tips']
    print(f"\n  竞品写作借鉴:")
    print(f"    - 标题风格: {tips.get('title_style_tip', '无')[:80]}")
    print(f"    - 开头技巧: {tips.get('opening_technique', '无')[:80]}")
    print(f"    - 避坑提醒: {tips.get('avoid_pitfall', '无')[:80]}")

step3_result = {
    'status': 'ok',
    'coverage': insights.get('coverage_level', 'unknown'),
    'covered_accounts': len(insights.get('covered_by', [])),
    'suggested_angles_count': len(insights.get('suggested_angles', []))
}


# ============================================================
# Step 4/8: 文章撰写 (Agent LLM真人写作)
# ============================================================
print("\n" + "="*60)
print("Step 4/8: 文章撰写 (Agent LLM)")
print("="*60)

from modules.article_generator import ArticleGenerator

gen = ArticleGenerator(CONFIG)

# 生成文章
article_result = gen.generate(
    topic=selected_topic_title,
    title=selected_topic_title,
    selected_title=None  # 让系统自己生成标题
)

# 处理输出
if isinstance(article_result, dict):
    article_data = article_result
elif hasattr(article_result, 'model_dump'):
    article_data = article_result.model_dump()
else:
    article_data = {
        'title': selected_topic_title,
        'content': str(viral_titles),
        'paragraphs': [{'type': 'body', 'text': str(viral_titles), 'bold_ranges': [], 'image_prompt': '', 'needs_image': True}]
    }

title = article_data.get('title', selected_topic_title)
paragraphs = article_data.get('paragraphs', [])
tags = article_data.get('tags', []) or []

# 如果没有段落，尝试从content拆分
if not paragraphs:
    content = article_data.get('content', '')
    if content:
        # 按换行或句号拆分
        parts = [p.strip() for p in content.split('\n') if p.strip()]
        paragraphs = [{'type': ('opening' if i == 0 else 'body' if i < len(parts)-1 else 'closing'),
                       'text': p, 'bold_ranges': [], 'image_prompt': '', 'needs_image': i == 0}
                     for i, p in enumerate(parts)]

# 为每个段落生成配图prompt（基于段落内容前100字）
max_total_images = int(CONFIG.get('IMAGES_PER_ARTICLE', 4) or 4)
max_total_images = max(1, min(max_total_images, 4))

for idx, p in enumerate(paragraphs):
    p_text = p.get('text', '')
    desc_base = p_text[:100].replace('\n', ' ').strip()

    if p.get('type') == 'opening':
        p['image_prompt'] = (
            f"A high-quality magazine cover about: {desc_base}. "
            f"Futuristic tech style, dark blue background, "
            f"digital particles, glowing elements, no people."
        )
        p['image_hint'] = '封面主视觉'
    elif p.get('type') in ('body', 'closing'):
        p['image_prompt'] = (
            f"Illustration depicting: {desc_base}. "
            f"Modern flat design style, clean composition, "
            f"tech-themed colors, informative visual, no people, no text overlay."
        )
        p['image_hint'] = f'第{idx+1}段配图'

    p['needs_image'] = idx > 0 and idx <= max_total_images - 1

total_chars = sum(len(p.get('text', '')) for p in paragraphs)
print(f"  [OK] 文章完成: 《{title}》")
print(f"       字数: {total_chars}, 段落数: {len(paragraphs)}")
if tags:
    print(f"       标签: {', '.join(tags[:5])}")

step4_result = {
    'status': 'ok',
    'title': title,
    'word_count': total_chars,
    'paragraph_count': len(paragraphs),
    'tags_count': len(tags)
}


# ============================================================
# Step 5/8: 文章数据记录 ★ 新增模块
# ============================================================
print("\n" + "="*60)
print("Step 5/8: 文章数据记录 (article_performance)")
print("="*60)

from modules.article_performance import ArticlePerformanceTracker

tracker = ArticlePerformanceTracker()

record = tracker.record_article({
    'article_title': title,
    'publish_date': datetime.now().strftime('%Y-%m-%d'),
    'topic': selected_topic_title,
    'title_template': title,  # 用实际标题
    'category': best_topic_data.get('matched_category', 'tech_general') if best_topic_data else 'tech_general',
    'word_count': total_chars,
    'paragraph_count': len(paragraphs),
    'image_count': sum(1 for p in paragraphs if p.get('needs_image')),
    'topic_score': selected_topic_score,
    'topic_grade': selected_topic_grade,
})

print(f"  [OK] 文章已记录:")
art_id = record.get('article_id') if isinstance(record, dict) else '?'
print(f"       ID: {art_id}")
print(f"       标题: {title[:50]}")
print(f"       话题: {selected_topic_title[:40]} ({selected_topic_grade}级/{selected_topic_score}分)")
print(f"       标签: {', '.join(tags[:5]) if tags else '无'}")
print(f"       状态: pending_publish (等待发表后录入阅读数据)")

step5_result = {
    'status': 'ok',
    'article_id': art_id,
    'title': title,
    'topic': selected_topic_title,
    'grade': selected_topic_grade,
}


# ============================================================
# Step 6/8: AI配图生成
# ============================================================
print("\n" + "="*60)
print("Step 6/8: AI配图生成")
print("="*60)

from modules.image_generator import ImageGenModule
img_gen = ImageGenModule(CONFIG)
images_dir = Path("output/images")
images_dir.mkdir(parents=True, exist_ok=True)

cover_path = None
para_images = []

safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_'))[:30]

# 6.1 封面图
print("  [封面] 生成中...")
try:
    cover_prompt = paragraphs[0].get('image_prompt',
        f"Magazine cover about: {title}. Futuristic technology style, glowing digital network.")
    cover_path = img_gen.generate_single(cover_prompt, size="1280x720", suffix="_cover")
    if cover_path:
        para_images.append(cover_path)
    print(f"  [OK] 封面: {Path(cover_path).name if cover_path else 'FAIL'}")
except Exception as e:
    print(f"  [WARN] 封面失败: {e}")

# 6.2 段落配图
for idx, p in enumerate(paragraphs):
    if not p.get('image_prompt') or not p.get('needs_image'):
        continue
    try:
        img_path = img_gen.generate_single(p['image_prompt'], size="1280x720", suffix=f"_p{idx}_{p.get('type','?')}")
        p['image_path'] = img_path
        para_images.append(img_path)
        print(f"  [OK] 段{idx+1}: {Path(img_path).name}")
    except Exception as e:
        print(f"  [WARN] 段{idx+1}失败: {e}")

valid_images = [p for p in para_images if p and os.path.exists(str(p))]
unique_names = set(Path(img).name for img in valid_images)

print(f"\n  [OK] 配图: 共{len(valid_images)}张, 唯一文件名={len(unique_names)}, 覆盖={len(unique_names)==len(valid_images)}")

step6_result = {
    'status': 'ok',
    'total_images': len(valid_images),
    'unique_files': len(unique_names),
    'all_unique': len(unique_names) == len(valid_images)
}


# ============================================================
# Step 7/8: HTML渲染
# ============================================================
print("\n" + "="*60)
print("Step 7/8: HTML渲染")
print("="*60)

html_content = build_html(title, paragraphs, cover_path)
ts = int(time.time())
safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '_'))[:40]
html_path = f"output/previews/preview_{safe_filename}_{ts}.html"

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

img_count = html_content.count('<img ')
embed_count = sum(1 for p in paragraphs if p.get('image_path'))
print(f"  [OK] HTML: {html_path}")
print(f"       图片: <img>={img_count}, 段落配图={embed_count}")

step7_result = {'status': 'ok', 'file': html_path, 'images': img_count}


# ============================================================
# Step 8/8: Playwright截图
# ============================================================
print("\n" + "="*60)
print("Step 8/8: Playwright截图")
print("="*60)

final_path = None
try:
    from playwright.sync_api import sync_playwright
    url = f"http://localhost:8080/output/previews/preview_{safe_filename}_{ts}.html"
    final_ts = int(time.time())
    final_path = f"output/previews/final_{final_ts}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 375, 'height': 812})
        page.goto(url, timeout=15000, wait_until='networkidle')
        page.wait_for_timeout(2000)
        page.screenshot(path=final_path, full_page=True)
        imgs_loaded = page.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            let ok = 0, fail = 0;
            imgs.forEach(img => { if(img.complete && img.naturalWidth>0) ok++; else fail++; });
            return {total: imgs.length, ok, fail};
        }""")
        browser.close()

    print(f"  [OK] 截图: {final_path}")
    print(f"       图片加载: 总计={imgs_loaded['total']}, 成功={imgs_loaded['ok']}, 失败={imgs_loaded['fail']}")

except ImportError:
    print("  [WARN] playwright未安装, 跳过截图")
except Exception as e:
    print(f"  [WARN] 截图异常: {e}")


# ============================================================
# 结果汇总
# ============================================================
print("\n" + "="*60)
print("流水线 v3 完成! 结果汇总")
print("="*60)

results = {
    'version': 'v3',
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'title': title,
    'steps': {
        'step1_hot_fetch': step1_result,
        'step2_topic_score': step2_result,
        'step3_competitor': step3_result,
        'step4_article_gen': step4_result,
        'step5_perf_record': step5_result,
        'step6_images': step6_result,
        'step7_html': step7_result,
        'step8_screenshot': final_path
    },
    'key_metrics': {
        'topics_fetched': step1_result.get('total', 0),
        'topics_scored': step2_result.get('scored_count', 0),
        'selected_grade': selected_topic_grade,
        'selected_score': selected_topic_score,
        'competitor_accounts_covered': step3_result.get('covered_accounts', 0),
        'word_count': total_chars,
        'images_generated': step6_result.get('total_images', 0),
        'article_id': art_id,
    }
}

print(json.dumps(results, ensure_ascii=False, indent=2, default=str))

result_json = f"output/flow_result.json"
with open(result_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n结果已保存: {result_json}")
