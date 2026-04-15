# -*- coding: utf-8 -*-
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.wechat_api import WeChatPublisher

CONFIG = yaml.safe_load((PROJECT_ROOT / "config.yaml").read_text(encoding="utf-8")) or {}
PREVIEW_DIR = PROJECT_ROOT / "output" / "previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
RUN_DIR = PROJECT_ROOT / "output" / "publish_runs"
RUN_DIR.mkdir(parents=True, exist_ok=True)

if len(sys.argv) < 3:
    raise SystemExit("usage: python _finalize_publish_payload.py <payload_json> <image_map_json>")

payload_path = Path(sys.argv[1])
image_map_path = Path(sys.argv[2])
payload = json.loads(payload_path.read_text(encoding="utf-8"))
image_map = json.loads(image_map_path.read_text(encoding="utf-8"))
article = payload["article"]
paragraphs = article.get("paragraphs", [])

cover_path = image_map.get("cover")
if cover_path:
    article["cover_image"] = cover_path

for para in paragraphs:
    idx = int(para.get("index", 0))
    img_path = image_map.get(f"p{idx}")
    if img_path:
        para["image_path"] = img_path


def to_rel(path_str):
    if not path_str:
        return ""
    path = Path(path_str).resolve()
    rel = path.relative_to((PROJECT_ROOT / "output").resolve())
    if rel.parts and rel.parts[0] == "images":
        return "../images/" + "/".join(rel.parts[1:])
    return str(path)



def build_preview_html(article):
    title = article.get("title", "")
    paragraphs = article.get("paragraphs", [])
    cover_html = ""
    if article.get("cover_image"):
        cover_html = f'<img src="{to_rel(article["cover_image"])}" class="cover-img" alt="封面">'

    blocks = []
    for para in paragraphs:
        text = para.get("text", "")
        block = [f'<div class="paragraph"><p>{text}</p>']
        if para.get("image_path"):
            block.append(f'<img src="{to_rel(para["image_path"])}" class="para-img" alt="配图">')
        block.append('</div>')
        blocks.append("".join(block))

    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;max-width:100%;padding:12px;color:#222;line-height:1.8}}
h1{{font-size:24px;line-height:1.4;margin:16px 0}}
.cover-img,.para-img{{width:100%;border-radius:10px;box-shadow:0 4px 14px rgba(0,0,0,.12);margin:12px 0}}
.paragraph{{margin-bottom:22px;font-size:17px}}
</style></head><body>{cover_html}<h1>{title}</h1>{''.join(blocks)}</body></html>'''

safe_title = ''.join(c for c in article.get('title', '未命名文章') if c.isalnum() or c in (' ', '_'))[:40]
ts = int(time.time())
html_path = PREVIEW_DIR / f"preview_publish_{safe_title}_{ts}.html"
html_path.write_text(build_preview_html(article), encoding="utf-8")

png_path = PREVIEW_DIR / f"final_publish_{ts}.png"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 375, "height": 812})
    page.goto(f"file:///{html_path.resolve().as_posix()}", wait_until="networkidle", timeout=20000)
    page.wait_for_timeout(1500)
    page.screenshot(path=str(png_path), full_page=True)
    browser.close()

publisher = WeChatPublisher(CONFIG)
publish_result = publisher.publish_article(article, publish_now=False)

result = {
    "payload_path": str(payload_path),
    "image_map_path": str(image_map_path),
    "html_path": str(html_path),
    "screenshot_path": str(png_path),
    "publish_result": publish_result,
    "title": article.get("title"),
    "published_at": datetime.now().isoformat(),
}
result_path = RUN_DIR / f"result_{ts}.json"
result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
