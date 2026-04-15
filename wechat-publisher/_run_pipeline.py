# -*- coding: utf-8 -*-
"""完整流程：热点抓取 → AI写文 → 配图(横版1280×720) → 预览 → 截图"""
import sys, os, json, time, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, 'images'), exist_ok=True)

print("=" * 60)
print("  爆款内容发布系统 - 完整流程")
print("=" * 60)

# ====== 步骤1: 抓取热点 ======
print("\n[步骤1/4] 抓取今日热点...")
from modules.hot_topics import HotTopicFetcher

config = {'HOT_SOURCES': [{'name': '今日头条', 'enabled': True}, {'name': '百度热搜', 'enabled': True}]}
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()

if not topics:
    print("ERROR: 未获取到热点，使用备用话题")
    TOPIC_TITLE = "GPT-5发布在即：AI将再次颠覆我们的认知"
else:
    if isinstance(topics, dict):
        items = list(topics.values())[:5]
    else:
        items = topics[:5] if isinstance(topics, list) else [topics]
    first_item = items[0] if items else {}
    if isinstance(first_item, dict):
        TOPIC_TITLE = first_item.get('title', first_item.get('name', str(first_item)))
    else:
        TOPIC_TITLE = str(first_item)
    print(f"抓取成功！共 {len(items)} 个热点")
    for i, t in enumerate(items):
        title = t.get('title', t.get('name', str(t))) if isinstance(t, dict) else str(t)
        print(f"  {i+1}. {title}")
    print(f"\n选中: {TOPIC_TITLE}")

# ====== 步骤2: AI撰写文章 ======
print("\n[步骤2/4] AI撰写文章...")
from modules.article_generator import ArticleGenerator

gen_config = {'WRITING_STYLE': 'entertaining_first_person', 'MAX_AI_SCORE': 40}
gen = ArticleGenerator(gen_config)
article = gen.generate(topic=TOPIC_TITLE, title=TOPIC_TITLE)

if article and isinstance(article, dict):
    article_title = article.get('title', TOPIC_TITLE)
    # paragraphs 是 list[dict]，每项有 'text' 键
    raw_paras = article.get('paragraphs', [])
    if not raw_paras:
        raw_paras = article.get('sections', [])
    # 提取纯文本列表
    sections_list = []
    for p in raw_paras:
        if isinstance(p, str):
            sections_list.append(p)
        elif isinstance(p, dict):
            text = p.get('text', p.get('content', str(p)))
            sections_list.append(text)
    if not sections_list:
        sections_list = ["（正文内容）"]
else:
    print("WARNING: 文章生成失败，使用模拟数据")
    article_title = TOPIC_TITLE
    sections_list = [
        "说实话，今天看到这个消息的时候，我第一反应是——又来了。",
        "但仔细想想，这次好像真的不太一样。",
        "以我的经验来看，每次技术革命到来之前，都有类似的征兆。",
        "最让我意外的是，这次连最保守的分析师都开始改口风了。",
        "当然，我们也要保持理性。技术再牛，落地才是关键。"
    ]
    article = {'title': TOPIC_TITLE}

print(f"文章标题: {article_title}")
print(f"段落数: {len(sections_list)}")

# ====== 步骤3: AI配图（横版1280×720）======
print("\n[步骤3/4] 生成AI配图（横版1280×720）...")

def gen_image(prompt, size="1280x720"):
    """调用 image_gen 工具生成单张图片"""
    try:
        from modules.image_generator import ImageGenModule
        img_mod = ImageGenModule({'IMAGE_STYLE': 'tech'})
        result = img_mod.generate_single(prompt=prompt, style='科技商业插画', size=size)
        return result
    except Exception as e:
        print(f"  [ImageGenModule失败: {e}] 尝试直接API...")
        try:
            # fallback: 用内置 image_helper
            import importlib.util
            ih_path = os.path.join(os.path.dirname(__file__), 'modules', 'image_helper.py')
            if os.path.exists(ih_path):
                spec = importlib.util.spec_from_file_location('image_helper', ih_path)
                ih = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ih)
                return ih.generate_image(prompt, os.path.join(OUTPUT_DIR, 'images'), f"img_{int(time.time())}.png", size)
        except Exception as e2:
            print(f"  全部失败: {e2}")
        return None

# 生成封面图
cover_prompt = f"{article_title} 杂志封面风格，中文标题，科技蓝色调，神经网络背景，高质量商业插画"
cover_img = gen_image(cover_prompt)
print(f"  封面图: {cover_img or '(生成失败，将用已有图片替代)'}")

# 生成段落配图
para_prompts = [
    f"{TOPIC_TITLE} 科技场景，未来数据中心服务器机房全息投影，科幻电影质感",
    f"{TOPIC_TITLE} 城市景观，新旧世界对比分屏效果，AR增强现实叠加",
    f"{TOPIC_TITLE} 概念可视化，宇宙星云中诞生的AI意识，数字粒子汇聚",
]
para_imgs = []
for idx, pp in enumerate(para_prompts):
    img = gen_image(pp)
    para_imgs.append(img)
    print(f"  段落图{idx+1}: {img or '(生成失败)'}")

# 如果图片生成失败，尝试复用已有的 output/images 中的图片
def get_existing_img(pattern):
    """从已有图片中找一张匹配的"""
    img_dir = os.path.join(OUTPUT_DIR, 'images')
    if os.path.exists(img_dir):
        for f in sorted(os.listdir(img_dir), reverse=True):
            if pattern in f.lower() or (pattern == '*' and f.endswith('.png')):
                full = os.path.join(img_dir, f)
                if os.path.getsize(full) > 10000:  # >10KB 才算有效图片
                    return full
    return None

if not cover_img:
    cover_img = get_existing_img('cover') or get_existing_img('gpt5') or get_existing_img('*')

for i in range(len(para_imgs)):
    if not para_imgs[i]:
        para_imgs[i] = get_existing_img('para') or get_existing_img('ai_') or get_existing_img('*')

print(f"\n  最终配图: 封面={os.path.basename(cover_img) if cover_img else '无'}, 段落={len([x for x in para_imgs if x])}张")

# ====== 步骤4: 生成公众号预览HTML ======
print("\n[步骤4/4] 生成公众号风格预览...")

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

sections_html = ""
for i, content in enumerate(sections_list):
    img_tag = ""
    if i < len(para_imgs) and para_imgs[i]:
        rel_path = os.path.basename(para_imgs[i])
        img_tag = f'\n<div class="img-wrap"><img src="./images/{rel_path}" class="article-img" alt="配图{i+1}"/></div>\n'
    sections_html += f'<div class="para">{content}</div>{img_tag}'

cover_img_rel = os.path.basename(cover_img) if cover_img else ""

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{article_title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,"PingFang SC","Helvetica Neue","Microsoft YaHei",sans-serif; background:#f5f5f5; color:#333; line-height:1.8; }}
.container {{ max-width:430px; margin:0 auto; background:#fff; min-height:100vh; }}
.cover {{ position:relative; width:100%; overflow:hidden; }}
.cover-img {{ width:100%; height:auto; display:block; }}
.title-area {{ padding:20px 18px 16px; border-bottom:1px solid #f0f0f0; }}
.title-area h1 {{ font-size:22px; font-weight:700; line-height:1.5; color:#1a1a1a; }}
.title-area .meta {{ font-size:12px; color:#999; margin-top:8px; display:flex; align-items:center; gap:12px; }}
.body {{ padding:16px 18px 40px; }}
.para {{ font-size:16px; margin-bottom:16px; text-align:justify; text-indent:2em; }}
.para:first-child {{ text-indent:0; font-weight:600; color:#1a1a1a; }}
.img-wrap {{ margin:16px -18px; }}
.article-img {{ width:100%; height:auto; display:block; }}
.footer {{ text-align:center; padding:30px 18px; color:#bbb; font-size:13px; border-top:1px solid #f0f0f0; margin-top:30px; }}
</style>
</head>
<body>
<div class="container">
<div class="cover">
  <img src="./images/{cover_img_rel}" class="cover-img"/>
</div>
<div class="title-area">
  <h1>{article_title}</h1>
  <div class="meta"><span>爆款工作室</span>·<span>{now}</span></div>
</div>
<div class="body">{sections_html}</div>
<div class="footer"><p>— END —</p><p style="margin-top:8px;">点击上方蓝字关注我们</p></div>
</div>
</body>
</html>'''

preview_path = os.path.join(OUTPUT_DIR, 'article_preview.html')
with open(preview_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n{'='*60}")
print("  流程完成！")
print(f"{'='*60}")
print(f"  热点:   {TOPIC_TITLE}")
print(f"  标题:   {article_title}")
print(f"  段落数: {len(sections_list)}")
print(f"  封面:   {os.path.basename(cover_img) if cover_img else '(未生成)'}")
print(f"  段落图: {len([x for x in para_imgs if x])}/{len(para_imgs)} 张")
print(f"  预览:   {preview_path}")
print(f"{'='*60}")
