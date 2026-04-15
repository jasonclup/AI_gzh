# -*- coding: utf-8 -*-
"""流水线 Step 3+4: 配图上传 + 推送草稿到公众号"""

import sys, os, json, yaml
sys.path.insert(0, os.path.dirname(__file__))

# 加载配置
config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 读取文章结果
article_path = os.path.join(os.path.dirname(__file__), '_pipeline_step2_result.json')
with open(article_path, 'r', encoding='utf-8') as f:
    article = json.load(f)

print(f'文章标题: {article["title"]}')

# === 分配AI生成的配图路径（本次用image_gen工具生成的）===
images_dir = os.path.join(os.path.dirname(__file__), 'output', 'images')

# 封面图（AI概念：科技消费）
article['cover_image'] = os.path.join(images_dir, 'Modern_tech_gadgets_smartphone_2026-04-15T09-28-21.png')

# 段落配图映射（段落 index -> 图片文件名）
para_images = {
    1: os.path.join(images_dir, 'Realistic_photograph_of_a_mode_2026-04-15T09-29-15.png'),     # 智能家居体验店
}

for para in article.get('paragraphs', []):
    idx = para.get('index')
    if idx in para_images and para.get('needs_image'):
        para['image_path'] = para_images[idx]
        print(f'  段落{idx}配图: {os.path.basename(para_images[idx])}')

# 验证图片存在
for key in ['cover_image']:
    p = article.get(key)
    if p and os.path.exists(p):
        print(f'[OK] 封面图存在: {os.path.basename(p)} ({os.path.getsize(p)//1024}KB)')
    else:
        print(f'[FAIL] 封面图缺失: {p}')
        
for para in article.get('paragraphs', []):
    ip = para.get('image_path', '')
    if ip and os.path.exists(ip):
        print(f'[OK] 段落{para["index"]}图存在: {os.path.basename(ip)} ({os.path.getsize(ip)//1024}KB)')

# 标题和摘要长度控制
# 实测未认证订阅号API：标题上限≈64字符(中文)，摘要上限≈120字符(中文)
# 不再激进截断，保留完整吸睛效果
title = article.get('title', '')[:64]
article['title'] = title

summary_full = article.get('summary', '')[:120]
article['summary'] = summary_full
print(f'最终标题: {article["title"]}')
print(f'最终摘要: {article["summary"]}')

# === 调用 WeChatPublisher 推草稿 ===
print('\n=== Step 3+4: 上传图片并推送草稿 ===')
from modules.wechat_api import WeChatPublisher

pub = WeChatPublisher(config)
if not pub.is_configured():
    print('ERROR: 公众号未配置！')
    sys.exit(1)

result = pub.publish_article(article, publish_now=False)
print(f'\n推送结果: {json.dumps(result, ensure_ascii=False, indent=2)}')

if result.get('media_id'):
    print(f'\n[OK] 草稿创建成功! media_id: {result["media_id"]}')
    print('请去 mp.weixin.qq.com 草稿箱查看')
else:
    print(f'\n[FAIL] 草稿创建失败: {result}')
