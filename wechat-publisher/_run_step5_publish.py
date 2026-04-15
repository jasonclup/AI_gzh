# -*- coding: utf-8 -*-
"""
Step 5: 群发发布（带原创声明）
从草稿升级为直接群发，支持多篇打包一次发送
用法: python _run_step5_publish.py [draft_media_id]
       不传参数则先保存新草稿再群发
"""
import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.wechat_api import WeChatPublisher


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_path):
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    raise FileNotFoundError(f"配置文件不存在: {config_path}")


def main():
    config = load_config()
    publisher = WeChatPublisher(config)
    
    # 读取最新文章数据（Step 2 输出）
    result_file = os.path.join(os.path.dirname(__file__), '_pipeline_step2_result.json')
    
    if not os.path.exists(result_file):
        print("[ERROR] 未找到 _pipeline_step2_result.json，请先运行 Step 1+2 生成文章")
        return
    
    with open(result_file, 'r', encoding='utf-8') as f:
        article = json.load(f)
    
    print(f'=" * 64)')
    print(f'Step 5: Group Publish (with Original Content Declaration)')
    print(f'Topic: {article.get("original_topic", "N/A")}')
    print(f'Title: {article.get("title", "N/A")}')
    print(f'Author: 往前看的月半子')
    print(f'Copyright: ON (original content declaration)')
    print(f'=" * 64)')
    
    images_dir = os.path.join(os.path.dirname(__file__), 'output', 'images')
    
    # 构建发布数据
    token = publisher._get_access_token()
    
    # 单篇文章包装成列表
    articles_data = {"articles": []}
    
    # 设置封面图和段落配图（与step4一致）
    article['cover_image'] = os.path.join(images_dir, 'Realistic_photograph_of_a_Huaw_2026-04-15T07-41-48.png')
    for para in article.get('paragraphs', []):
        idx = para.get('index', 0)
        if idx == 1:
            para['image_path'] = os.path.join(images_dir, 'Smartphone_retail_store_with_g_2026-04-15T07-43-55.png')
    
    for idx, art in enumerate([article]):
        title = article.get('title', '')
        
        # 构建HTML正文
        html_content = ''
        paragraphs = article.get('paragraphs', [])
        for para in paragraphs:
            text = para.get('text', '').replace('\n', '<br/>')
            
            # **粗体** -> 高亮strong标签
            import re
            def _highlight_bold(m):
                return f'<strong style="color:#c0392b;font-weight:bold;background:linear-gradient(transparent 60%,#ffeaa7 0);">{m.group(1)}</strong>'
            text = re.sub(r'\*\*(.+?)\*\*', _highlight_bold, text)
            
            p_style = "font-size:16px;line-height:1.8;color:#333;margin-bottom:20px;letter-spacing:0.5px;text-align:justify;"
            html_content += f'<p style="{p_style}">{text}</p>'
            
            # 配图
            img_path = para.get('image_path', '')
            if img_path and os.path.exists(img_path):
                try:
                    img_url = publisher.upload_temp_image(img_path)
                    img_style = "width:100%;border-radius:8px;margin-bottom:20px;display:block;"
                    html_content += f'<p><img src="{img_url}" style="{img_style}" mode="widthFix"/></p>'
                except Exception as e:
                    print(f'[WARN] Image upload failed para{para.get("index")}: {e}')
        
        # 关注引导CTA
        cta_style = "background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:25px 20px;border-radius:12px;text-align:center;margin-top:30px;"
        html_content += f'<section style="{cta_style}"><p style="color:white;font-size:18px;font-weight:bold;margin-bottom:10px;">关注我，每天分享最新资讯</p><p style="color:rgba(255,255,255,0.9);font-size:14px;">科技 / 汽车 / 社会热点深度解读</p></section></section>'
        
        # 封面图上传（永久素材，返回media_id）
        cover_path = article.get('cover_image', '')
        if cover_path and os.path.exists(cover_path):
            cover_media_id = publisher.upload_image(cover_path)  # 永久素材
        else:
            print(f'[WARN] Article {idx+1} cover not found: {cover_path}')
            continue
        
        # 截断标题和摘要
        t = article.get('title', '')
        t_enc = t.encode('utf-8')
        if len(t_enc) > 64:
            t = t_enc[:64].decode('utf-8', errors='ignore')
        
        s = article.get('summary', '')
        s_enc = s.encode('utf-8')
        if len(s_enc) > 120:
            s = s_enc[:120].decode('utf-8', errors='ignore')
        
        art_entry = {
            "title": t,
            "author": "往前看的月半子",
            "digest": s,
            "content": html_content,
            "thumb_media_id": cover_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
            "content_source_url": "",
            "copyright_stat": 1,  # 原创声明
        }
        articles_data["articles"].append(art_entry)
        
        print(f'  [{idx+1}] {t}')
    
    if not articles_data["articles"]:
        print("[ERROR] No valid articles to publish")
        return
    
    # 第一步：保存为草稿
    print('\n[Step 5a] Saving draft...')
    import requests
    draft_url = f"{publisher.BASE_URL}/cgi-bin/draft/add?access_token={token}"
    resp = requests.post(
        draft_url,
        data=json.dumps(articles_data, ensure_ascii=False).encode('utf-8'),
        headers={'Content-Type': 'application/json; charset=utf-8'},
        timeout=30
    )
    draft_result = resp.json()
    
    if 'media_id' not in draft_result:
        print(f"[ERROR] Draft failed: {json.dumps(draft_result, ensure_ascii=False)}")
        return
    
    media_id = draft_result['media_id']
    print(f'[OK] Draft saved! media_id: {media_id}')
    
    # 第二步：确认是否真的要群发
    print(f'\n{"=" * 64}')
    print(f'PUBLISH CONFIRMATION')
    print(f'Media ID: {media_id}')
    print(f'Articles : {len(articles_data["articles"])}')
    print(f'WARNING : This will PUBLISH to all followers immediately!')
    print(f'{"=" * 64}')
    
    # 直接执行群发（订阅号限制：每天仅1次）
    print('\n[Step 5b] Publishing...')
    publish_url = f"{publisher.BASE_URL}/cgi-bin/freepublish/submit?access_token={token}"
    pub_resp = requests.post(publish_url, json={"media_id": media_id}, timeout=30)
    pub_result = pub_resp.json()
    
    print(f'\nPublish Result:')
    print(json.dumps(pub_result, ensure_ascii=False, indent=2))
    
    if 'publish_id' in pub_result or 'msg_id' in pub_result:
        print(f'\n[PUBLISHED] Success!')
        print(f'- publish_id: {pub_result.get("publish_id", "N/A")}')
        print(f'- Check status: https://mp.weixin.qq.com -> Published Articles')
        
        # 保存发布记录
        pub_log = {
            "published_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "media_id": media_id,
            "publish_id": pub_result.get('publish_id', ''),
            "article_count": len(articles_data["articles"]),
            "titles": [a['title'] for a in articles_data["articles"]],
        }
        log_path = os.path.join(os.path.dirname(__file__), 'output', 'publish_log.jsonl')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(pub_log, ensure_ascii=False) + '\n')
        print(f'[OK] Log saved: {log_path}')
    else:
        print(f'\n[PUBLISH FAILED] Error code: {pub_result.get("errcode", "unknown")}')


if __name__ == '__main__':
    main()
