# -*- coding: utf-8 -*-
"""完整流程测试 + 输出到文件"""
import sys, os, json, time, yaml, traceback

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher"
sys.path.insert(0, PROJECT_ROOT)

OUT_DIR = r"C:\Users\v_junshshi\WorkBuddy\Claw\output"
LOG_PATH = os.path.join(OUT_DIR, 'flow_result.json')

def log(msg):
    print(msg)
    with open(os.path.join(OUT_DIR, 'flow_console.log'), 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# 清空旧日志
with open(os.path.join(OUT_DIR, 'flow_console.log'), 'w', encoding='utf-8') as f:
    f.write('')

log("=== 开始完整流程 ===")

# 加载配置
config_path = os.path.join(PROJECT_ROOT, 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# === 步骤1: 抓取热点 ===
log("[1/4] 抓取热点话题...")
from modules.hot_topics import HotTopicFetcher
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()
if not topics:
    log("[ERR] 没有抓到热点!")
    sys.exit(1)

topic = topics[0] if isinstance(topics[0], dict) else {'title': str(topics[0])}
topic_text = topic.get('title', topic.get('name', str(topic)))
log(f"[OK] 热点: {topic_text}")

# === 步骤2: 生成文章 ===
log("[2/4] AI生成文章...")
from modules.article_generator import ArticleGenerator
article_gen = ArticleGenerator(config)
article = article_gen.generate(
    topic=topic_text,
    title=topic_text,
    selected_title=None,
    extra_context='',
)
log(f"[OK] 文章: {article.get('title','?')}")
log(f"     字数: {article.get('word_count',0)}, 段落: {len(article.get('paragraphs',[]))}")

# === 步骤3: 生成配图 ===
log("[3/4] 生成配图...")
from modules.image_generator import ImageGenModule
img_gen = ImageGenModule(config)

t0 = time.time()
try:
    article_with_images = img_gen.generate_for_article(article)
    elapsed = time.time() - t0
    log(f"[OK] 配图完成! 耗时 {elapsed:.1f}s")
except Exception as e:
    log(f"[ERR] 配图失败: {e}")
    traceback.print_exc()
    article_with_images = article

# 收集图片信息
result = {
    'topic': topic_text,
    'title': article_with_images.get('title', ''),
    'cover_image': article_with_images.get('cover_image', ''),
    'paragraphs': [],
    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
}

if article_with_images.get('cover_image'):
    cp = article_with_images['cover_image']
    sz = os.path.getsize(cp) if os.path.exists(cp) else 0
    result['cover_size'] = sz
    log(f"     封面: {cp} ({sz//1024}KB)")

for p in article_with_images.get('paragraphs', []):
    pi = {'index': p.get('index', 0), 'text': p.get('text', '')[:200]}
    if p.get('image_path'):
        ip = p['image_path']
        sz = os.path.getsize(ip) if os.path.exists(ip) else 0
        pi['image_path'] = ip
        pi['image_size'] = sz
        log(f"     段{p['index']+1}: {ip} ({sz//1024}KB)")
    result['paragraphs'].append(pi)

# 保存结果JSON
with open(LOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
log(f"\n[OK] 结果已保存: {LOG_PATH}")
log("=== 流程完成 ===")
