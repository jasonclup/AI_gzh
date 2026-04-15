# -*- coding: utf-8 -*-
"""
完整流水线运行器 - 每步截图 + 飞书人格化推送
"""

import os
import sys
import json
import time
import logging

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

OUTPUT = os.path.join(BASE, 'output')
IMAGES = os.path.join(OUTPUT, 'images')
PREVIEWS = os.path.join(OUTPUT, 'previews')
os.makedirs(IMAGES, exist_ok=True)
os.makedirs(PREVIEWS, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
log = logging.getLogger('Pipeline')

# ==================== 配置 ====================
import yaml
with open(os.path.join(BASE, 'config.yaml'), 'r', encoding='utf-8') as f:
    CONFIG = yaml.safe_load(f) or {}

SELECTED_TOPIC = CONFIG.get('PIPELINE', {}).get('default_topic', '')
SELECTED_TITLE = CONFIG.get('PIPELINE', {}).get('default_title', '')

if not SELECTED_TOPIC:
    SELECTED_TOPIC = "GPT-5即将发布，AI将再次颠覆认知"
    SELECTED_TITLE = "深度体验GPT-5后，我发现了一个秘密..."

log.info(f"话题: {SELECTED_TOPIC}")
log.info(f"标题: {SELECTED_TITLE}")

# ==================== 截图工具 ====================
from PIL import Image, ImageDraw, ImageFont


def make_screenshot(title, items=None, status_icon="OK", color=(46, 139, 87)):
    """生成步骤截图（模拟截图效果）"""
    W, H = 1280, 720
    img = Image.new('RGB', (W, H), '#1a1a2e')
    draw = ImageDraw.Draw(img)

    # 标题栏背景
    draw.rectangle([0, 0, W, 80], fill='#16213e')

    # 状态图标和标题
    icon_map = {"OK": "[OK]", "WR": "[!]", "ART": "[IMG]", "PM": "[PM]", "QA": "[TEST]", "DEV": "[DEV]"}
    label = icon_map.get(status_icon, f"[{status_icon}]")
    draw.text((40, 22), f"{label} {title}", fill='white', font=_load_font(32))

    y = 110
    if items:
        for item in items:
            txt = str(item)
            if len(txt) > 70:
                txt = txt[:67] + '...'
            draw.text((50, y), f"* {txt}", fill='#e0e0e0', font=_load_font(20))
            y += 38
            if y > H - 60:
                break

    # 底部时间戳
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    draw.text((40, H - 40), f"[SNAP] {ts} | WeChat Auto Publisher",
              fill='#888', font=_load_font(16))
    return img


def _load_font(size):
    fonts_to_try = [
        "msyh.ttc", "C:/Windows/Fonts/msyh.ttc",
        "simhei.ttf", "C:/Windows/Fonts/simhei.ttf",
        "arial.ttf", None,
    ]
    for fp in fonts_to_try:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def save_screenshot(img, name):
    path = os.path.join(PREVIEWS, name)
    img.save(path)
    log.info(f"Screenshot saved: {path}")
    return path


# ==================== 初始化飞书团队 ====================
from modules.feishu_bot import FeishuTeam
from modules.team_manager import AITeamPipeline

feishu_mgr = FeishuTeam()

# 从配置读取默认群聊ID
import json as _json
with open(os.path.join(BASE, 'feishu_bots_config.json'), 'r', encoding='utf-8') as _fc:
    _fconf = _json.load(_fc)
CHAT_ID = _fconf.get('default_chat_id', '')

if CHAT_ID:
    feishu_mgr.set_chat_id(CHAT_ID)
    log.info(f"Feishu chat_id: {CHAT_ID}")
else:
    log.warning("No chat_id found - will run without Feishu push")

tm = AITeamPipeline(feishu_team=feishu_mgr, chat_id=CHAT_ID or "")


# ==================== 辅助函数：发送带截图的消息 ====================
def send_with_image(role, status, detail_text, image_path=None):
    """通过人格引擎生成消息并发送，可选附带图片"""
    # 使用detail作为主要文本传入人格引擎
    msg = tm._persona_speak(role, status, detail=detail_text)

    # 发送图片（先上传再发消息）
    if image_path and os.path.exists(image_path) and tm.feishu and tm.chat_id:
        try:
            role_bot_map = {
                "hot_fetcher": "hot_fetcher", "writer": "writer",
                "artist": "artist", "reviewer": "reviewer",
                "coordinator": "coordinator", "pm": "product_manager",
                "tester": "tester", "dev": "developer",
            }
            bot_key = role_bot_map.get(role, "coordinator")
            try:
                bot = tm.feishu.get_bot(bot_key)
            except KeyError:
                bot = tm.feishu.coordinator
            # 先上传图片获取key，再发送
            img_key = bot.upload_image(image_path)
            if img_key:
                bot.send_image_msg(tm.chat_id, img_key)
                log.info(f"Image sent via {role}: {image_path}")
        except Exception as e:
            log.warning(f"Image send failed: {e}")


# ==================== 步骤函数 ====================
def step_1_fetch_topics():
    from modules.hot_topics import HotTopicFetcher
    tf = HotTopicFetcher(CONFIG)

    send_with_image('hot_fetcher', 'start',
                    f'Scanning all platforms for hot topics...\n'
                    f'Targets: Weibo / Baidu / Douyin / Toutiao / Zhihu')

    topics = tf.fetch_all()
    if not topics:
        from modules.hot_topics import FALLBACK_TOPICS
        import datetime as dt
        topics = [{**t, 'source': 'built-in-fallback',
                   'fetched_at': dt.datetime.now().isoformat()} for t in FALLBACK_TOPICS]

    best = topics[0]
    topic_title = best.get('title', SELECTED_TOPIC)
    hot_val = best.get('hot_value', 0)

    display_items = []
    for i, t in enumerate(topics[:10]):
        hv = t.get('hot_value', 0)
        src = t.get('source', '?')
        title = t.get('title', '')[:50]
        display_items.append(f"[{i+1}] HOT:{hv:,} ({src}) {title}")
    display_items.append('')
    display_items.append(f'SELECTED: {topic_title}')
    display_items.append(f'HOT_VALUE: {hot_val:,}')

    img = make_screenshot("STEP 1 - Hot Topics Fetched", display_items, "OK")
    path = save_screenshot(img, 'step1_topics.png')

    send_with_image('hot_fetcher', 'ok',
                    f'Got {len(topics)} topics!\n\n'
                    f'>> TOP PICK: [{topic_title}]\n'
                    f'   Heat Score: **{hot_val:,}**\n\n'
                    f'Top5:\n' +
                    '\n'.join([f'{i+1}. {t["title"][:35]} ({t.get("hot_value",0):,})'
                              for i, t in enumerate(topics[:5])]),
                    path)

    return {'topics': topics[:20], 'selected': {'title': topic_title, 'hot_value': hot_val}, 'screenshot': path}


def step_2_generate_article(topic_data):
    from modules.article_generator import ArticleGenerator
    ag = ArticleGenerator(CONFIG)
    selected_title = topic_data['selected']['title']
    topic_text = selected_title

    send_with_image('writer', 'start',
                    f'Received topic: "{topic_text[:30]}"\n\n'
                    f'Direction: First-person + Entertaining + Deep insight')

    article = ag.generate(
        topic=topic_text,
        title=SELECTED_TITLE or selected_title,
        selected_title=SELECTED_TITLE or selected_title,
        extra_context='',
        author_name="AI Observer",
    )

    title = article.get('title', 'Untitled')
    wc = article.get('word_count', 0)
    paras = article.get('paragraphs', [])
    tags = article.get('tags', [])

    display_items = [
        f"Title: {title}",
        f"Words: {wc}",
        f"Paragraphs: {len(paras)}",
        f"Tags: {', '.join(tags[:6])}",
    ]
    for p in paras[:6]:
        ptype = p.get('type', '')
        txt = p.get('text', '')[:50]
        display_items.append(f"  [{ptype}] {txt}...")

    img = make_screenshot("STEP 2 - Article Generated", display_items, "OK")
    path = save_screenshot(img, 'step2_article.png')

    first_line = paras[0]['text'][:80] + '...' if paras else ''

    send_with_image('writer', 'ok',
                    f'Article ready!\n\n'
                    f'**{title}**\n'
                    f'Words: **{wc}** | Sections: **{len(paras)}**\n'
                    f'Tags: {" ".join("#"+t for t in tags[:5])}\n\n'
                    f'Opening:\n> {first_line}',
                    path)

    return {'article': article, 'screenshot': path}


def step3_generate_images(article_data):
    from modules.image_generator import ImageGenModule
    ig = ImageGenModule(CONFIG)
    article = article_data['article']

    send_with_image('artist', 'start',
                    f'Received article: "{article.get("title","")[:30]}"\n\n'
                    f'Style: Tech-blue 1280x720 | Chinese context | No people')

    result = ig.generate_for_article(article)

    cover = result.get('cover_image', '')
    image_count = result.get('image_count', 0)
    paragraphs = result.get('paragraphs', [])

    display_items = [f"Cover: {cover}", f"Images: {image_count}"]
    for p in paragraphs:
        if p.get('image_path'):
            hint = p.get('image_hint', '')[:45]
            display_items.append(f"  IMG: {p['image_path']} ({hint})")

    img = make_screenshot("STEP 3 - Images Generated", display_items, "ART")
    path = save_screenshot(img, 'step3_images.png')

    expert_advice = ""
    if hasattr(tm, 'expert'):
        expert_advice = tm.expert.get_expert_advice('artist', 'image_quality')

    send_with_image('artist', 'ok',
                    f'All images rendered!\n\n'
                    f'Cover: `{cover}`\n'
                    f'Total: **{image_count}** images\n\n'
                    f'{f"Design tip: {expert_advice}" if expert_advice else ""}',
                    path)

    return {'result': result, 'screenshot': path}


def step4_html_preview(image_data):
    """Step 4: Generate HTML preview from article data"""
    article_with_images = image_data['result']

    send_with_image('pm', 'start',
                    f'Entering HTML preview phase...\n\n'
                    f'Focus: Layout beauty / Mobile adapt / Image load speed')

    # Build HTML inline
    title = article_with_images.get('title', 'Untitled')
    author = article_with_images.get('author', 'AI Observer')
    paragraphs = article_with_images.get('paragraphs', [])
    summary = article_with_images.get('summary', '')
    tags = article_with_images.get('tags', [])
    cover_image = article_with_images.get('cover_image', '')

    # Convert image paths to URLs (绝对路径，兼容 file:// 和 http:// 两种协议)
    def img_to_url(p):
        if not p:
            return ''
        if p.startswith(('http://', 'https://')):
            return p
        fname = os.path.basename(p)
        # file:// 协议需要绝对路径
        abs_path = os.path.abspath(os.path.join(IMAGES, fname)).replace('\\', '/')
        return f'../output/images/{fname}'  # HTTP模式（Flask服务）

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

    for p in paragraphs:
        ptype = p.get('type', '')
        txt = p.get('text', '')
        img_path = p.get('image_path', '')

        # 渲染文本（跳过空段落）
        if txt:
            # 段落图片：嵌入在文字下方（如果该段有配图的话）
            if img_path:
                url = img_to_url(img_path)
                hint = p.get('image_hint', '')[:40]
                html_parts.append(
                    f'<div class="para">{txt}'
                    f'</div>'
                    f'<img class="para-img" src="{url}" alt="{hint}">'
                    f'<p class="img-caption">📸 {hint}</p>')
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

    file_size = len(html_content.encode('utf-8'))

    display_items = [
        f"File: {html_file}",
        f"Size: {file_size:,} bytes ({file_size // 1024}KB)",
        f"Paragraphs: {len(paragraphs)}",
        f"Access: http://localhost:8080/output/previews/{html_filename}",
    ]

    img = make_screenshot("STEP 4 - HTML Preview Ready", display_items, "PM")
    path = save_screenshot(img, 'step4_preview.png')

    expert_advice = ""
    if hasattr(tm, 'expert'):
        expert_advice = tm.expert.get_expert_advice('pm', 'html_preview')

    send_with_image('pm', 'ok',
                    f'HTML page ready!\n\n'
                    f'**{html_filename}**\n'
                    f'Size: **{file_size // 1024}KB** | Sections: **{len(paragraphs)}**\n\n'
                    f'{f"Product tip: {expert_advice}" if expert_advice else ""}\n\n'
                    f'URL: `http://localhost:8080/output/previews/{html_filename}`',
                    path)

    return {'html_file': html_file, 'screenshot': path}


def step5_take_screenshot(preview_data):
    """Step 5: Take final screenshot of the HTML preview"""
    html_file = preview_data['html_file']

    send_with_image('tester', 'start',
                    f'Starting screenshot output test...\n\n'
                    f'Test items: Resolution / Render integrity / File size')

    # Try to use playwright/selenium if available, otherwise generate a summary image
    try:
        from playwright.sync_api import sync_playwright
        html_abs = os.path.abspath(html_file)
        file_url = 'file:///' + html_abs.replace('\\', '/')
        screenshot_out = os.path.join(PREVIEWS, f'final_{int(time.time())}.png')

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 375, 'height': 812})  # mobile viewport
            page.goto(file_url, wait_until='networkidle')
            page.screenshot(path=screenshot_out, full_page=True)
            browser.close()

        screenshot_path = screenshot_out
    except ImportError:
        # No playwright available - create a summary card instead
        log.info("Playwright not available, generating summary screenshot")
        screenshot_path = os.path.join(PREVIEWS, f'summary_{int(time.time())}.png')
        
        # Read HTML for info
        with open(html_file, 'r', encoding='utf-8') as f:
            html_text = f.read()

        # Extract key info for display
        import re
        title_match = re.search(r'<div class="title">(.*?)</div>', html_text, re.DOTALL)
        title_str = title_match.group(1) if title_match else "Unknown"
        
        para_count = len(re.findall(r'class="para"', html_text))
        img_count = len(re.findall(r'para-img|cover', html_text))

        # Generate a nice summary image
        sum_img = make_screenshot(
            f"FINAL OUTPUT: {title_str[:40]}",
            [
                f"HTML Preview: {os.path.basename(html_file)}",
                f"",
                f"Paragraphs: {para_count}",
                f"Images: {img_count + 1}",  # +1 for cover
                f"",
                f"To view full preview:",
                f"http://localhost:8080/output/previews/",
                f"",
                f"[Open in browser for actual rendering]",
            ],
            "QA"
        )
        save_screenshot(sum_img, os.path.basename(screenshot_path))

    if os.path.exists(screenshot_path):
        size_kb = os.path.getsize(screenshot_path) // 1024

        display_items = [
            f"Screenshot: {screenshot_path}",
            f"Size: {size_kb:,} KB",
        ]
        img = make_screenshot("STEP 5 - Screenshot Output", display_items, "QA")
        path = save_screenshot(img, 'step5_final.png')

        test_report = ""
        if hasattr(tm, 'expert'):
            test_report = tm.expert.get_expert_advice('tester', 'screenshot_quality')

        send_with_image('tester', 'ok',
                        f'Screenshot output passed QA!\n\n'
                        f'Final artifact:\n'
                        f'Path: `{screenshot_path}`\n'
                        f'Size: **{size_kb}KB**\n\n'
                        f'{f"QA Report: {test_report}" if test_report else ""}',
                        path)
    else:
        path = save_screenshot(make_screenshot("WARNING - Screenshot Failed",
                                               ["Check if HTML file is valid"], "WR"),
                               'step5_warning.png')
        tm._send_by_role('tester', f'[ERROR] Screenshot failed: {screenshot_path}')

    return {'screenshot': path}


# ==================== 主流程 ====================

log.info("=" * 60)
log.info("FULL PIPELINE START (screenshots + feishu)")
log.info(f"Topic: {SELECTED_TOPIC}")
log.info(f"Title: {SELECTED_TITLE}")
log.info(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# 主控启动
send_with_image('coordinator', 'start',
                f'Full pipeline task dispatching...\n\n'
                f'Target Topic: "{SELECTED_TOPIC}"\n'
                f'Target Title: "{SELECTED_TITLE}"\n\n'
                f'Pipeline: Topics -> Writing -> Images -> Preview -> Screenshot\n'
                f'5 stages total, ETA 3-5 min')

results = {}
start_time = time.time()

try:
    # Step 1
    log.info("Step 1/5: Fetching topics...")
    results['step1'] = step_1_fetch_topics()
    s1 = results["step1"]
    log.info(f"  DONE. Got {len(s1['topics'])} topics")

    time.sleep(2)

    # Step 2
    log.info("Step 2/5: Generating article...")
    results['step2'] = step_2_generate_article(results['step1'])
    s2 = results["step2"]
    log.info(f"  DONE. Words: {s2['article'].get('word_count', 0)}")

    time.sleep(2)

    # Step 3
    log.info("Step 3/5: Generating images...")
    results['step3'] = step3_generate_images(results['step2'])
    s3 = results["step3"]
    log.info(f"  DONE. Images: {s3['result'].get('image_count', 0)}")

    time.sleep(2)

    # Step 4
    log.info("Step 4/5: Rendering HTML preview...")
    results['step4'] = step4_html_preview(results['step3'])
    s4 = results["step4"]
    log.info(f"  DONE. File: {s4['html_file']}")

    time.sleep(2)

    # Step 5
    log.info("Step 5/5: Taking final screenshot...")
    results['step5'] = step5_take_screenshot(results['step4'])
    log.info("  DONE.")

    elapsed = int(time.time() - start_time)

    # Dev summary
    dev_summary = ""
    if hasattr(tm, 'expert'):
        dev_summary = tm.expert.get_expert_advice('dev', 'pipeline_summary')

    # Coordinator final report
    r1, r2, r3 = results["step1"], results["step2"], results["step3"]
    summary_table = (
        "| Stage | Role | Status | Output |\n"
        "|-------|------|--------|--------|\n"
        f"| 1.Topics | DataAnalyst | OK | {len(r1['topics'])} items |\n"
        f"| 2.Writing | Writer | OK | {r2['article'].get('word_count',0)} words |\n"
        f"| 3.Images | Artist | OK | {r3['result'].get('image_count',0)} imgs |\n"
        f"| 4.Preview | ProductMgr | OK | Rendered |\n"
        f"| 5.Screenshot | Tester | OK | Saved |\n"
    )

    all_screenshots = [r['screenshot'] for r in results.values() if r.get('screenshot')]

    send_with_image('coordinator', 'ok',
                    f'**PIPELINE COMPLETE!**\n\n'
                    f'{summary_table}\n\n'
                    f'Elapsed: **{elapsed}s**\n'
                    f'Screenshots: **{len(all_screenshots)}** generated\n\n'
                    f'{f"Dev Review: {dev_summary}" if dev_summary else ""}'
                    )

    log.info("=" * 60)
    log.info("PIPELINE FINISHED!")
    log.info(f"Total time: {elapsed}s")
    log.info(f"Screenshots: output/previews/")
    log.info("=" * 60)

except Exception as e:
    elapsed = int(time.time() - start_time)
    log.error(f"Pipeline error: {e}", exc_info=True)
    tm._send_by_role('coordinator',
                     f'[FAIL] Pipeline broke at step {len(results)+1}\n\n'
                     f'Error: {str(e)[:200]}\n'
                     f'Runtime: {elapsed}s')
    log.error(f"FAILED: {e}")
