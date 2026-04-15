# -*- coding: utf-8 -*-
"""
完整5步内容生产流水线（无飞书版，含截图）
- 每个步骤完成后生成截图
- 配图根据每段文案内容自动生成匹配的图片
- 最终输出 Playwright 手机端截图
"""

import sys
import os
import io

# Fix Windows console encoding for emoji/Chinese
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import json
import time
import random
from datetime import datetime
from pathlib import Path

# 项目根目录（脚本已在 wechat-publisher/ 内）
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 加载配置
import yaml
config_path = PROJECT_ROOT / 'config.yaml'
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        CONFIG = yaml.safe_load(f) or {}
else:
    CONFIG = {}


def build_html(title, paragraphs, cover_path=None):
    """构建移动端适配的HTML文章页面（封面图+段落配图）"""
    def to_rel(p):
        if not p: return ''
        pp = Path(p).resolve()
        # 图片在 output/images/，HTML在 output/previews/
        # 正确相对路径: ../images/xxx.png
        try:
            rel = pp.relative_to(PROJECT_ROOT.resolve())
            parts = list(rel.parts)
            # output/images/xxx.png → ../images/xxx.png (从 previews/ 出发)
            if len(parts) >= 2 and parts[0] == 'output' and parts[1] == 'images':
                return '../images/' + '/'.join(parts[2:])  # ../images/filename
            # 其他情况用绝对路径格式(供http://访问)
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
            hint = p.get('image_hint', '')
            hint_html = f'<p class="img-caption">{hint}</p>' if hint else ''
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

os.chdir(PROJECT_ROOT)

def step_screenshot(step_name, data=None):
    """生成步骤截图（文字版）"""
    ts = int(time.time())
    filename = f"output/previews/{step_name}_{ts}.png"

    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (900, 500), '#1a1a2e')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        font = ImageFont.truetype("arial.ttf", 18)
        small = ImageFont.truetype("arial.ttf", 14)
    except:
        try:
            title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
        except:
            title_font = ImageFont.load_default()
            font = ImageFont.load_default()
            small = ImageFont.load_default()

    draw.text((40, 30), f"Step: {step_name}", fill='#00d4ff', font=title_font)
    draw.text((40, 80), f"Time: {datetime.now().strftime('%H:%M:%S')}", fill='#888888', font=small)

    if isinstance(data, list):
        draw.text((40, 120), f"Items: {len(data)}", fill='#00ff88', font=font)
        y = 160
        for item in data[:8]:
            text = str(item)[:80]
            draw.text((40, y), text, fill='#cccccc', font=small)
            y += 24
    elif isinstance(data, dict):
        y = 120
        for k, v in list(data.items())[:10]:
            text = f"{k}: {str(v)[:60]}"
            draw.text((40, y), text, fill='#cccccc', font=small)
            y += 26
    elif isinstance(data, str):
        lines = data.split('\n')
        y = 120
        for line in lines[:12]:
            draw.text((40, y, 900-40, y+22), line[:90], fill='#cccccc', font=small)
            y += 22

    draw.rectangle([(30, 10), (870, 480)], outline='#333355', width=2)
    img.save(filename)
    print(f"  📸 截图已保存: {filename} ({img.size[0]}x{img.size[1]})")
    return filename


def image_screenshot(step_name, image_paths):
    """生成图片展示截图"""
    ts = int(time.time())
    filename = f"output/previews/{step_name}_{ts}.png"

    from PIL import Image as PILImage

    n = len(image_paths)
    if n == 0:
        return step_screenshot(f"{step_name}_empty", {"status": "no images"})

    cols = min(n, 2)
    rows = (n + cols - 1) // cols
    thumb_w, thumb_h = 420, 236

    canvas = PILImage.new('RGB', (900, 60 + rows * (thumb_h + 50)), '#1a1a2e')

    for i, path in enumerate(image_paths):
        if not os.path.exists(path):
            continue
        try:
            img = PILImage.open(path).convert('RGB').resize((thumb_w, thumb_h))
            col = i % cols
            row = i // cols
            x = 30 + col * (thumb_w + 20)
            y = 30 + row * (thumb_h + 50)
            canvas.paste(img, (x, y))
        except Exception as e:
            print(f"  ⚠️ 图片加载失败: {path}: {e}")

    canvas.save(filename)
    print(f"  📸 图片展示截图: {filename}")
    return filename


# ============================================================
# Step 1: 热点抓取
# ============================================================
print("\n" + "="*60)
print("🚀 Step 1/5: 热点抓取")
print("="*60)

from modules.hot_topics import HotTopicFetcher
fetcher = HotTopicFetcher(CONFIG)
topics = fetcher.fetch_all()
print(f"  ✅ 获取到 {len(topics)} 条热点")
for t in topics[:5]:
    print(f"     - [{t.get('heat','?')}] {t.get('title','?')[:50]}")

s1_file = step_screenshot("step1_topics", topics)


# ============================================================
# Step 2: 文章撰写（每段附带场景描述用于配图）
# ============================================================
print("\n" + "="*60)
print("✍️  Step 2/5: 文章撰写")
print("="*60)

from modules.article_generator import ArticleGenerator
gen = ArticleGenerator(CONFIG)

topic = topics[0] if topics else {"title": "AI技术突破引发全局关注"}
topic_title = topic.get('title', topic) if isinstance(topic, dict) else str(topic)

# 生成爆款标题
viral_titles = gen.get_viral_titles(topic_title) if hasattr(gen, 'get_viral_titles') else [topic_title]
selected_title = viral_titles[0] if viral_titles else topic_title

# 生成文章
article_result = gen.generate(
    topic=topic_title,
    title=selected_title,
    selected_title=selected_title
)

if isinstance(article_result, dict):
    article_data = article_result
elif hasattr(article_result, 'model_dump'):
    article_data = article_result.model_dump()
else:
    article_data = {
        'title': str(article_result),
        'content': str(article_result),
        'paragraphs': [{'type': 'body', 'text': str(article_result)}]
    }

title = article_data.get('title', '未命名文章')
paragraphs = article_data.get('paragraphs', [])

total_chars = sum(len(p.get('text', '')) for p in paragraphs)
print(f"  ✅ 文章完成: 《{title}》")
print(f"     字数: {total_chars}, 段落数: {len(paragraphs)}")

# 为每个段落生成配图描述（基于段落内容）
max_total_images = int(CONFIG.get('IMAGES_PER_ARTICLE', 4) or 4)
max_total_images = max(1, min(max_total_images, 4))
for idx, p in enumerate(paragraphs):
    p_text = p.get('text', '')
    # 截取前100字作为图片描述基础
    desc_base = p_text[:100].replace('\n', ' ').strip()

    if p.get('type') == 'opening':
        # 开头段落 → 封面风格
        p['image_prompt'] = (
            f"A high-quality magazine cover about: {desc_base}. "
            f"Futuristic tech style, dark blue background, "
            f"digital particles, glowing elements, no people."
        )
        p['image_hint'] = '封面主视觉'
    elif p.get('type') in ('body', 'closing'):
        # 正文/结尾段落 → 内容匹配插图
        p['image_prompt'] = (
            f"Illustration depicting: {desc_base}. "
            f"Modern flat design style, clean composition, "
            f"tech-themed colors, informative visual, no people, no text overlay."
        )
        p['image_hint'] = f'第{idx+1}段配图 - 场景插画'

    # 统一约束：每篇总配图 1~4 张（含封面）
    p['needs_image'] = idx > 0 and idx <= max_total_images - 1
    print(f"     段落[{p.get('type','?')}]: {len(p.get('text',''))}字 → 配图prompt已生成 | needs_image={p.get('needs_image')}")

s2_file = step_screenshot("step2_article", {
    'title': title,
    'chars': total_chars,
    'paragraphs': len(paragraphs),
    'max_total_images': max_total_images,
    'has_image_prompts': all(p.get('image_prompt') for p in paragraphs)
})



# ============================================================
# Step 3: 配图生成（使用每段的 image_prompt）
# ============================================================
print("\n" + "="*60)
print("🎨  Step 3/5: AI配图生成")
print("="*60)

from modules.image_generator import ImageGenModule
img_gen = ImageGenModule(CONFIG)
images_dir = Path("output/images")
images_dir.mkdir(parents=True, exist_ok=True)

cover_path = None
para_images = []

safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_'))[:30]

# 3.1 封面图
print("  [封面] 生成中...")
try:
    cover_prompt = paragraphs[0].get('image_prompt',
        f"Magazine cover about: {title}. Futuristic technology style, glowing digital network.")
    print(f"      prompt[:100]: {cover_prompt[:100]}")
    cover_path = img_gen.generate_single(cover_prompt, size="1280x720", suffix="_cover")
    if cover_path:
        para_images.append(cover_path)
    print(f"  ✅ 封面图: {cover_path}")
except Exception as e:
    print(f"  ⚠️ 封面图失败: {e}")

# 3.2 段落配图（仅为 needs_image=true 的段落生成，保证总量 1~4 张含封面）
for idx, p in enumerate(paragraphs):
    if not p.get('image_prompt') or not p.get('needs_image'):
        continue
    print(f"  [段落{idx+1}] 根据文案内容生成配图中...")
    try:
        img_path = img_gen.generate_single(p['image_prompt'], size="1280x720", suffix=f"_p{idx}_{p.get('type','?')}")
        p['image_path'] = img_path
        para_images.append(img_path)
        print(f"  ✅ 段落{idx+1}配图: {img_path}")
    except Exception as e:
        print(f"  ⚠️ 段落{idx+1}配图失败: {e}")


valid_images = [p for p in para_images if p and os.path.exists(str(p))]
print(f"\n  ✅ 配图完成: 共生成 {len(valid_images)} 张图片")

# 验证：检查文件名是否全部唯一（无覆盖）
unique_names = set(Path(img).name for img in valid_images)
dup_warning = ""
if len(unique_names) != len(valid_images):
    dup_warning = f" ⚠️ 文件名重复! {len(valid_images)}张图只有{len(unique_names)}个不同文件名"
else:
    dup_warning = f" ✅ {len(unique_names)}个独立文件名，无覆盖"

for img in valid_images:
    size_kb = os.path.getsize(str(img)) // 1024
    print(f"     🖼️ {Path(img).name} ({size_kb}KB)")
print(f"{dup_warning}")

s3_files = image_screenshot("step3_images", valid_images)


# ============================================================
# Step 4: HTML渲染（封面图 + 段落配图嵌入）
# ============================================================
print("\n" + "="*60)
print("📄 Step 4/5: HTML渲染")
print("="*60)

html_content = build_html(title, paragraphs, cover_path)
ts = int(time.time())
safe_filename = "".join(c for c in title if c.isalnum() or c in (' ', '_'))[:40]
html_path = f"output/previews/preview_{safe_filename}_{ts}.html"
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

img_count = html_content.count('<img ')
embed_count = sum(1 for p in paragraphs if p.get('image_path'))
print(f"  ✅ HTML已保存: {html_path}")
print(f"     嵌入图片: <img>标签={img_count}, 段落配图={embed_count}")

s4_file = step_screenshot("step4_html", {'file': html_path, 'images': img_count, 'path_embed': embed_count})


# ============================================================
# Step 5: Playwright截图
# ============================================================
print("\n" + "="*60)
print("📱 Step 5/5: Playwright截图")
print("="*60)

final_path = None
try:
    from playwright.sync_api import sync_playwright

    url = f"http://localhost:8080/output/previews/preview_{safe_filename}_{ts}.html"
    final_ts = int(time.time())

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 375, 'height': 812})
        page.goto(url, timeout=15000, wait_until='networkidle')
        page.wait_for_timeout(2000)

        final_path = f"output/previews/final_{final_ts}.png"
        page.screenshot(path=final_path, full_page=True)

        imgs_loaded = page.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            let ok = 0, fail = 0;
            imgs.forEach(img => { if(img.complete && img.naturalWidth>0) ok++; else fail++; });
            return {total: imgs.length, ok, fail};
        }""")

        browser.close()

    print(f"  ✅ 截图完成: {final_path}")
    print(f"     图片加载: 总计={imgs_loaded['total']}, 成功={imgs_loaded['ok']}, 失败={imgs_loaded['fail']}")

except ImportError:
    print("  ⚠️ playwright 未安装，跳过浏览器截图")
except Exception as e:
    print(f"  ⚠️ 截图异常: {e}")


# ============================================================
# 结果汇总
# ============================================================
print("\n" + "="*60)
print("🏁 流水线完成！结果汇总")
print("="*60)

results = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'title': title,
    'steps': [
        {'name': '热点抓取', 'status': '✅', 'count': len(topics)},
        {'name': '文章撰写', 'status': '✅', 'chars': total_chars},
        {'name': '配图生成', 'status': '✅', 'images': len(valid_images)},
        {'name': 'HTML渲染', 'status': '✅', 'file': html_path},
        {'name': 'Playwright截图', 'status': '✅', 'file': final_path}
    ],
    'files': [s1_file, s2_file, s3_files, s4_file, final_path],
    'preview_url': f"http://localhost:8080/output/previews/"
}

print(json.dumps(results, ensure_ascii=False, indent=2))

result_json = f"output/flow_result.json"
with open(result_json, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\n💾 结果已保存: {result_json}")
