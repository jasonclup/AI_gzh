# -*- coding: utf-8 -*-
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.article_generator import ArticleGenerator
from modules.hot_topics import HotTopicFetcher

CONFIG = yaml.safe_load((PROJECT_ROOT / "config.yaml").read_text(encoding="utf-8")) or {}
OUT_DIR = PROJECT_ROOT / "output" / "publish_runs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clamp_image_total(value):
    try:
        value = int(value)
    except Exception:
        value = 4
    return max(1, min(value, 4))


def build_cover_prompt(title, topic, opening_text):
    desc = (opening_text or title or topic)[:100].replace("\n", " ").strip()
    return (
        f"中文科技媒体封面插画，主题围绕：{title}。结合这段文案内容：{desc}。"
        f"画面要求：科技感、未来感、横版16:9、适合微信公众号头图、无人物、无脸、无人手、无文字。"
    )


def build_para_prompt(topic, para, idx):
    desc = para.get("text", "")[:100].replace("\n", " ").strip()
    hint = para.get("image_hint", "")
    return (
        f"中文科技文章配图，第{idx+1}段，主题：{topic}。"
        f"请根据这段文案生成画面：{desc}。"
        f"补充线索：{hint}。"
        f"要求：横版16:9，贴合中文语境，无人物、无脸、无人手、无文字、非海报、非重复构图。"
    )


fetcher = HotTopicFetcher(CONFIG)
try:
    topics = fetcher.fetch_all()
except Exception:
    topics = []

if not topics:
    print(json.dumps({
        "error": "NO_TOPICS_AVAILABLE",
        "message": "All hot topic sources failed. Cannot generate article without valid topics.",
        "suggestion": "Check network connectivity or source configuration in config.yaml"
    }, ensure_ascii=False, indent=2))
    sys.exit(2)

topic = topics[0]
topic_title = topic.get("title", str(topic))

gen = ArticleGenerator(CONFIG)
viral_titles = gen.get_viral_titles(topic_title) if hasattr(gen, "get_viral_titles") else [topic_title]
selected_title = viral_titles[0] if viral_titles else topic_title
article = gen.generate(topic=topic_title, title=selected_title, selected_title=selected_title)
if hasattr(article, "model_dump"):
    article = article.model_dump()

paragraphs = article.get("paragraphs", [])
max_total_images = clamp_image_total(CONFIG.get("IMAGES_PER_ARTICLE", 4))
max_para_images = max_total_images - 1
selected_para_indexes = []
for para in paragraphs:
    idx = int(para.get("index", 0))
    if idx > 0 and idx <= max_para_images:
        para["needs_image"] = True
        selected_para_indexes.append(idx)
    else:
        para["needs_image"] = False

image_jobs = [{
    "slot": "cover",
    "target": "cover_image",
    "size": "1280x720",
    "prompt": build_cover_prompt(article.get("title", ""), topic_title, paragraphs[0].get("text", "") if paragraphs else topic_title)
}]

for para in paragraphs:
    if not para.get("needs_image"):
        continue
    idx = int(para.get("index", 0))
    image_jobs.append({
        "slot": f"p{idx}",
        "target": f"paragraphs.{idx}.image_path",
        "paragraph_index": idx,
        "size": "1280x720",
        "prompt": build_para_prompt(topic_title, para, idx)
    })

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
payload = {
    "created_at": datetime.now().isoformat(),
    "topic": topic,
    "article": article,
    "max_total_images": max_total_images,
    "image_jobs": image_jobs,
    "selected_para_indexes": selected_para_indexes,
}
payload_path = OUT_DIR / f"payload_{ts}.json"
payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

summary = {
    "payload_path": str(payload_path),
    "title": article.get("title"),
    "topic": topic_title,
    "paragraph_count": len(paragraphs),
    "max_total_images": max_total_images,
    "selected_para_indexes": selected_para_indexes,
    "image_job_count": len(image_jobs),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
