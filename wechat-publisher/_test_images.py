# -*- coding: utf-8 -*-
"""
快速配图验证：只跑 Step 2(文章) + Step 3(配图) + Step 4(HTML) + Step 5(截图)
不推送飞书，专注解决"文章里没配图"的问题
"""

import os, sys, json, time, logging

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

OUTPUT = os.path.join(BASE, 'output')
IMAGES = os.path.join(OUTPUT, 'images')
PREVIEWS = os.path.join(OUTPUT, 'previews')
os.makedirs(IMAGES, exist_ok=True)
os.makedirs(PREVIEWS, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger('ImgTest')

import yaml
with open(os.path.join(BASE, 'config.yaml'), 'r', encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f) or {}

TOPIC = "GPT-5即将发布，AI将再次颠覆认知"
TITLE = "深度体验GPT-5后，我发现了一个秘密..."

log.info(f"[TEST] Topic: {TOPIC}")
log.info(f"[TEST] Title: {TITLE}")

# ========== Step 2: 文章生成 ==========
from modules.article_generator import ArticleGenerator

ag = ArticleGenerator(CONFIG)
article = ag.generate(
    topic=TOPIC,
    title=TITLE,
    selected_title=TITLE,
    author_name="AI Observer",
)

log.info(f"[Step2] 文章: {article['title']}, {article['word_count']}字, {len(article['paragraphs'])}段")

for i, p in enumerate(article['paragraphs']):
    log.info(f"  段{i} [{p['type']}] needs_image={p.get('needs_image')} image_hint={p.get('image_hint','')[:50]}")

# ========== Step 3: 配图生成 ==========
from modules.image_generator import ImageGenModule

ig = ImageGenModule(CONFIG)
result = ig.generate_for_article(article)

cover = result.get('cover_image', '')
img_count = result.get('image_count', 0)
paras = result['paragraphs']

log.info(f"[Step3] 封面: {cover}")
log.info(f"[Step3] 配图数: {img_count}")
for p in paras:
    if p.get('image_path'):
        log.info(f"  段{p['index']} 图片: {p['image_path']}")

# ========== Step 4: HTML预览（修复版） ==========
title = result['title']
author = result.get('author', 'AI Observer')
paragraphs = result['paragraphs']
tags = result.get('tags', [])
cover_image = result.get('cover_image', '')

def img_to_url(p):
    if not p:
        return ''
    if p.startswith(('http://', 'https://')):
        return p
    # 使用绝对路径，确保 file:// 协议下能正常加载
    return os.path.abspath(p).replace('\\', '/')

cover_url = img_to_url(cover_image)

html_parts = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
              '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
              '<style>'
              'body{max-width:680px;margin:0 auto;padding:20px;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;color:#333;background:#fff}'
              '.cover{width:100%;border-radius:8px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,0.1)}'
              '.title{font-size:24px;font-weight:bold;line-height:1.4;margin:16px 0}'
              '.meta{color:#888;font-size:14px;margin-bottom:20px}'
              '.para{font-size:17px;line-height:1.8;margin:18px 0;text-indent:2em}'
              '.para-img{width:100%;border-radius:6px;margin:12px 0;box-shadow:0 2px 10px rgba(0,0,0,0.08)}'
              '.img-caption{text-align:center;color:#999;font-size:13px;margin:-6px 0 14px 0;font-style:italic}'
              '.tags{margin-top:30px;color:#576b95;font-size:14px}'
              '.tag{margin-right:10px}'
              '</style></head><body>']

if cover_url:
    html_parts.append(f'<img class="cover" src="{cover_url}" alt="cover">')
html_parts.append(f'<div class="title">{title}</div>')
html_parts.append(f'<div class="meta">作者：{author}</div>')

# 关键修复：检查 image_path 而不是 type=='image'
embedded_images = 0
for p in paragraphs:
    ptype = p.get('type', '')
    txt = p.get('text', '')
    img_path = p.get('image_path', '')

    if txt:
        if img_path:
            url = img_to_url(img_path)
            hint = p.get('image_hint', '')[:40]
            html_parts.append(
                f'<div class="para">{txt}'
                f'</div>'
                f'<img class="para-img" src="{url}" alt="{hint}">'
                f'<p class="img-caption">📸 {hint}</p>')
            embedded_images += 1
        else:
            html_parts.append(f'<div class="para">{txt}</div>')

if tags:
    tag_html = ' '.join([f'<span class="tag">#{t}</span>' for t in tags])
    html_parts.append(f'<div class="tags">{tag_html}</div>')

html_parts.append('</body></html>')

html_content = '\n'.join(html_parts)
safe_title = title.replace(' ', '_')[:30]
ts = int(time.time())
html_filename = f'preview_{safe_title}_{ts}.html'
html_file = os.path.join(PREVIEWS, html_filename)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

log.info(f"[Step4] HTML: {html_file}")
log.info(f"[Step4] 嵌入图片: {embedded_images} 张 + 1张封面")

# ========== Step 5: Playwright截图 ==========
try:
    from playwright.sync_api import sync_playwright
    html_abs = os.path.abspath(html_file)
    file_url = 'file:///' + html_abs.replace('\\', '/')
    screenshot_out = os.path.join(PREVIEWS, f'final_imgtest_{int(time.time())}.png')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 375, 'height': 812})
        page.goto(file_url, wait_until='networkidle')
        
        # 验证图片加载情况
        imgs_loaded = page.evaluate('''() => {
            const imgs = document.querySelectorAll('.para-img, .cover');
            let loaded = 0;
            let failed = 0;
            imgs.forEach(img => {
                if (img.naturalWidth > 0) loaded++;
                else failed++;
            });
            return { total: imgs.length, loaded, failed };
        }''')
        
        log.info(f"[Step5] 图片加载: 总计={imgs_loaded['total']}, 成功={imgs_loaded['loaded']}, 失败={imgs_loaded['failed']}")

        page.screenshot(path=screenshot_out, full_page=True)
        browser.close()

    log.info(f"[Step5] 截图保存: {screenshot_out}")
    print(f"\n{'='*60}")
    print(f"RESULT: OK")
    print(f"  HTML:   {html_file}")
    print(f"  截图:   {screenshot_out}")
    print(f"  嵌入图片: {embedded_images} 张段落配图 + 封面")
    print(f"  加载状态: {imgs_loaded['loaded']}/{imgs_loaded['total']}")
    print(f"{'='*60}")

except ImportError:
    log.warning("Playwright未安装，跳过截图")
    print(f"\nHTML已生成: {html_file}")
    print(f"请用浏览器打开查看配图效果")

except Exception as e:
    log.error(f"截图失败: {e}", exc_info=True)
    print(f"\nERROR: {e}")
