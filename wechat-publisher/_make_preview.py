# -*- coding: utf-8 -*-
"""生成微信公众号风格文章预览"""
import json, os, time

RESULT_PATH = r"c:\Users\v_junshshi\WorkBuddy\Claw\output\flow_result.json"
OUTPUT_HTML = r"c:\Users\v_junshshi\WorkBuddy\Claw\output\article_preview.html"

with open(RESULT_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

topic = data.get('topic', '')
title = data.get('title', '')
paragraphs = data.get('paragraphs', [])
cover = data.get('cover_image', '')

# 构建段落HTML
para_html = ''
for i, p in enumerate(paragraphs):
    text = p.get('text', '').replace('\n', '<br/>')
    img = p.get('image_path', '')
    
    para_html += f'''<div class="para">
        <div class="text">{text}</div>
'''
    if img and os.path.exists(img):
        # 转为相对路径显示
        rel_img = os.path.basename(img)
        para_html += f'<img src="./images/{rel_img}" class="article-img" alt="配图{i+1}"/>'
    para_html += '</div>'

cover_html = ''
if cover and os.path.exists(cover):
    cover_html = f'<img src="./images/{os.path.basename(cover)}" class="cover-img"/>'

now = time.strftime('%Y-%m-%d %H:%M')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>{title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: #f5f5f5; font-family: -apple-system, "PingFang SC", "Helvetica Neue", sans-serif;
  max-width: 600px; margin: 0 auto; padding: 20px 16px; color:#333;
}}
.header-bg {{
  background: linear-gradient(135deg, #1a237e, #283593);
  border-radius: 12px; padding: 24px 20px; margin-bottom: 20px;
  color: #fff;
}}
.header-tag {{ font-size:12px; opacity:0.8; margin-bottom:8px; }}
.title {{ font-size:22px; font-weight:bold; line-height:1.4; }}
.cover-img {{ width:100%; border-radius:10px; margin-bottom:16px; box-shadow:0 4px 16px rgba(0,0,0,0.15); }}
.para {{ margin-bottom:20px; line-height:1.8; font-size:16px; color:#333; text-align:justify; }}
.text {{ margin-bottom:14px; }}
.article-img {{ width:100%; border-radius:8px; margin-top:10px; box-shadow:0 2px 12px rgba(0,0,0,0.1); }}
.highlight-box {{
  background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-left:4px solid #1565c0;
  padding:14px 16px; border-radius:0 8px 8px 0; margin:18px 0; font-size:15px; color:#0d47a1;
}}
.tag-line {{ text-align:center; padding:20px 0; color:#999; font-size:13px; border-top:1px solid #eee; margin-top:30px; }}
h2.section-title {{ 
  color: #1565c0; font-size:18px; margin:24px 0 12px; padding-left:12px;
  border-left:4px solid #4caf50; font-weight:600;
}}
</style>
</head>
<body>

<div class="header-bg">
  <div class="header-tag">📱 公众号爆款内容发布系统 · AI自动生成</div>
  <div class="title">✨ {title}</div>
</div>

{cover_html}

<div class="highlight-box">
  🔥 热点话题：{topic}<br/>
  📅 生成时间：{now}<br/>
  🤖 AI写作 + 自动配图（竖屏1080×1920）
</div>

<h2 class="section-title">📝 正文内容</h2>

{para_html}

<div class="tag-line">
  — 以上内容由AI辅助创作，仅供参考 —<br/>
  💡 觉得有用？欢迎点赞转发
</div>

</body>
</html>'''

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Preview generated: {OUTPUT_HTML}")
print(f"Title: {title}")
print(f"Paragraphs: {len(paragraphs)}")
