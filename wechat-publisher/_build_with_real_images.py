"""用 image_gen 生成的真正AI图片重建HTML + 截图"""
import sys, os, glob, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.chdir(r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher')

# 1. 找到最新HTML和文章数据
htmls = sorted(glob.glob('output/previews/preview_*.html'), key=os.path.getmtime, reverse=True)
latest_html = htmls[0] if htmls else None

with open('output/flow_result.json', 'r', encoding='utf-8') as f:
    flow = json.load(f)
title = flow.get('title', '')

# 2. 找到所有 image_gen 生成的图片（按时间排序）
real_imgs = sorted(glob.glob('output/images/*2026-04-14T11-4*.png'), key=os.path.getmtime)
print(f"Found {len(real_imgs)} real AI images:")
for i, img in enumerate(real_imgs):
    size_kb = os.path.getsize(img) // 1024
    print(f"  [{i}] {os.path.basename(img)} ({size_kb}KB)")

# 3. 读原文HTML获取文章段落内容
with open(latest_html, 'r', encoding='utf-8') as f:
    html_text = f.read()

# 提取段落（简单方式：从原HTML中找 para-text div的内容）
import re
paragraphs_html = re.findall(r'<div class="para-text">(.*?)</div>', html_text, re.DOTALL)

# 4. 构建新HTML：封面 + 每段配真实AI图
cover_img = real_imgs[0] if len(real_imgs) > 0 else ''
para_imgs = real_imgs[1:] if len(real_imgs) > 1 else []

# 图片路径转换为相对于 previews 目录的相对路径
def to_rel(path):
    abs_path = os.path.abspath(path).replace('\\', '/')
    # 从 output/previews/ 到 output/images/ 需要 ../images/
    basename = os.path.basename(abs_path)
    return f'../images/{basename}'

HTML_TEMPLATE = r'''<html>
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
.footer {{ margin-top:30px; padding-top:15px; border-top:1px solid #eee; font-size:12px; color:#aaa; text-align:center; }}
</style>
</head>
<body>
{cover_html}
<h1>{title}</h1>
{paragraphs_block}
<div class="footer">Powered by AI Content Pipeline | Generated {timestamp}</div>
</body>
</html>'''

# 封面
cover_rel = to_rel(cover_img) if cover_img else ''
cover_html = f'<img class="cover-img src="{cover_rel}" alt="cover">' if cover_rel else ''

# 段落
para_blocks = []
p_types = ['opening'] + ['body'] * (len(paragraphs_html)-2) + ['closing']
for i, (ptext_raw, ptype) in enumerate(zip(paragraphs_html, p_types)):
    ptext = ptext_raw.strip()
    # 清理HTML标签只保留纯文本
    clean_text = re.sub(r'<[^>]+>', '', ptext)

    # 配图
    img_html = ''
    if i < len(para_imgs):
        img_rel = to_rel(para_imgs[i])
        hints = ['', '数据中心服务器场景', 'AI大模型能力飞跃可视化', 
                 'AI改变普通人生活场景', '未来科技展望', 'AI革命浪潮']
        hint = hints[i+1] if i+1 < len(hints) else f'第{i}段配图'
        img_html = f'''
<div class="para-img-wrap">
  <img class="para-img" src="{img_rel}" alt="{hint}">
  <div class="img-caption">{hint}</div>
</div>'''

    block = f'''<div class="paragraph para-{ptype}">
<div class="para-text">{clean_text}</div>
{img_html}
</div>'''
    para_blocks.append(block)

final_html = HTML_TEMPLATE.format(
    title=title,
    cover_html=cover_html.replace('<img class="cover-img src=', '<img class="cover-img" src='),
    paragraphs_block='\n'.join(para_blocks),
    timestamp=time.strftime('%Y-%m-%d %H:%M')
)

# 保存新HTML
ts = int(time.time())
safe_title = title[:40].replace('/', '_')
out_html = f'output/previews/preview_{safe_title}_{ts}_REAL.html'
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(final_html)
print(f'\nHTML saved: {out_html}')
print(f'Images embedded: cover=1 + paragraphs={min(len(para_imgs), len(paragraphs_html))}')

# 5. Playwright 截图
import asyncio
from playwright.async_api import async_playwright

async def screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 375, 'height': 812})
        abs_path = os.path.abspath(out_html).replace('\\', '/')
        await page.goto(f'file:///{abs_path}', wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(5000)  # 等待大图加载

        out_png = f'output/previews/FULL_REAL_{ts}.png'
        await page.screenshot(path=out_png, full_page=True)
        size = os.path.getsize(out_png) / 1024
        
        # 验证图片加载状态
        loaded = await page.evaluate('''() => {
            const imgs = document.querySelectorAll('.para-img, .cover-img');
            let ok = 0, fail = 0;
            imgs.forEach(img => {
                if(img.naturalWidth > 0) ok++; else fail++;
            });
            return {total:imgs.length, ok, fail};
        }''')
        
        print(f'Screenshot: {out_png} ({size:.0f}KB)')
        print(f'Image load: total={loaded["total"]}, loaded={loaded["ok"]}, broken={loaded["fail"]}')
        await browser.close()

asyncio.run(screenshot())
print('\nDONE!')
