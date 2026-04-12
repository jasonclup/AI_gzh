# -*- coding: utf-8 -*-
"""完整流程测试：热点抓取 -> 文章生成 -> AI配图 -> 截图"""
import sys, os, json, asyncio, time, yaml

# Windows控制台UTF-8输出
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 确保项目根目录在路径中
PROJECT_ROOT = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher"
sys.path.insert(0, PROJECT_ROOT)

from modules.hot_topics import HotTopicFetcher
from modules.article_generator import ArticleGenerator
from modules.image_generator import ImageGenModule

# 加载配置
config_path = os.path.join(PROJECT_ROOT, 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

print("=" * 60)
print(" [FLOW] 开始完整流程测试")
print("=" * 60)

# === 步骤1: 抓取热点 ===
print("\n[1/4] 抓取热点话题...")
fetcher = HotTopicFetcher(config)
topics = fetcher.fetch_all()
if not topics:
    print("[ERR] 没有抓到热点!")
    sys.exit(1)

topic = topics[0] if isinstance(topics[0], dict) else {'title': str(topics[0])}
topic_text = topic.get('title', topic.get('name', str(topic)))
print(f"[OK] 选中热点: {topic_text}")

# === 步骤2: 生成文章 ===
print("\n[2/4] AI生成文章...")
article_gen = ArticleGenerator(config)
article = article_gen.generate(
    topic=topic_text,
    title=topic_text,
    selected_title=None,
    extra_context='',
)
print(f"[OK] 文章生成完成: {article.get('title','?')}")
print(f"     字数: {article.get('word_count',0)}, 段落数: {len(article.get('paragraphs',[]))}")

# 打印每段的image_hint，验证差异化
print("\n     [HINT] 各段配图提示:")
for p in article.get('paragraphs', []):
    if p.get('needs_image'):
        print(f"       段{p['index']+1}: {p.get('image_hint','')[:50]}")

# === 步骤3: 生成配图（核心测试）===
print("\n[3/4] 生成配图...")
img_gen = ImageGenModule(config)

# 打印封面prompt（is_cover=True）
cover_prompt = img_gen._build_semantic_prompt(topic_text, article.get('title',''), 
                                              hint=article.get('title',''), 
                                              para_text=article.get('title',''), is_cover=True)
print(f"\n     [PROMPT] 封面 prompt: {cover_prompt[:120]}...")

# 打印各段落prompt（验证是否不同）-- 核心验证点!
print("\n     [PROMPT] 各段 prompt (应不同):")
all_prompts = []
for p in article.get('paragraphs', []):
    if p.get('needs_image'):
        pp = img_gen._build_semantic_prompt(topic_text, title=article.get('title',''),
                                            hint=p['image_hint'], para_text=p['text'][:140])
        all_prompts.append(pp)
        print(f"       段{p['index']+1}: {pp[:100]}...")

# 检查是否有重复
unique_prompts = set(all_prompts)
if len(unique_prompts) != len(all_prompts):
    print("\n     [WARN] 存在重复的prompt!")
else:
    print(f"\n     [OK] 所有{len(all_prompts)}个段落prompt均不重复!")

# 执行实际图片生成
t0 = time.time()
article_with_images = img_gen.generate_for_article(article)
elapsed = time.time() - t0

print(f"\n     [OK] 配图生成完成! 耗时 {elapsed:.1f}s, 共 {article_with_images.get('image_count',0)} 张")

# 输出图片文件信息
generated_files = []
if article_with_images.get('cover_image'):
    cp = article_with_images['cover_image']
    sz = (os.path.getsize(cp)//1024) if os.path.exists(cp) else 0
    status = f"{sz}KB" if sz > 0 else "FILE_NOT_FOUND"
    print(f"     [IMG] 封面: {cp} ({status})")
    if sz > 0: generated_files.append(cp)

for p in article_with_images.get('paragraphs', []):
    if p.get('image_path'):
        ip = p['image_path']
        sz = (os.path.getsize(ip)//1024) if os.path.exists(ip) else 0
        status = f"{sz}KB" if sz > 0 else "FILE_NOT_FOUND"
        print(f"     [IMG] 段{p['index']+1}: {ip} ({status})")
        if sz > 0: generated_files.append(ip)

# 验证文件大小差异
if len(generated_files) >= 2:
    sizes = [os.path.getsize(f) for f in generated_files]
    unique_sizes = len(set(sizes))
    print(f"\n     [VERIFY] 文件大小: {sizes}, 不同大小数: {unique_sizes}/{len(sizes)}")
    if unique_sizes == len(sizes):
        print("     [OK] 所有图片文件大小均不同 => 图片内容确实不同!")

# === 步骤4: 截图预览 ===
print("\n[4/4] 启动浏览器截图...")
try:
    from playwright.async_api import async_playwright
    
    async def do_screenshot():
        # 启动Flask服务器（如果还没运行）
        from web.app import create_app
        app = create_app()
        
        import threading
        def run_flask():
            app.run(host='127.0.0.1', port=8080, use_reloader=False, debug=False)
        
        t = threading.Thread(target=run_flask, daemon=True)
        t.start()
        
        await asyncio.sleep(3)
        
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1440, 'height': 900})
            
            url = 'http://127.0.0.1:8080/editor'
            
            # 注入数据后导航
            article_json = json.dumps(article_with_images, ensure_ascii=False)
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(500)
            
            await page.evaluate(f'''() => {{
                const data = {json.dumps(article_json)};
                sessionStorage.setItem('draftArticle', JSON.stringify(data));
            }}''')
            
            await page.goto(url, timeout=15000)
            await page.wait_for_timeout(2500)
            
            out_dir = r"C:\Users\v_junshshi\WorkBuddy\Claw\output"
            os.makedirs(out_dir, exist_ok=True)
            shot_path = os.path.join(out_dir, f'flow_{time.strftime("%H%M%S")}.png')
            await page.screenshot(path=shot_path, full_page=False)
            
            print(f"     [OK] 截图已保存: {shot_path}")
            return shot_path
            
            await browser.close()
    
    result = asyncio.run(do_screenshot())
    
except Exception as e:
    print(f"     [WARN] 截图失败（非关键）: {e}")

print("\n" + "=" * 60)
print(" [DONE] 流程测试完成!")
print("=" * 60)
