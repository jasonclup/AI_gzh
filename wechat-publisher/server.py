# -*- coding: utf-8 -*-
"""
Minimal standalone server for WeChat Publisher.
Only loads what's needed per request - no heavy init.
Runs fast, never blocks on external calls.
"""

import os
import sys
import json
import logging
import random
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['JSON_AS_ASCII'] = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('server')

# === FALLBACK TOPICS (always available, no network needed) ===
FALLBACK_TOPICS = [
    {'title': 'GPT-5发布在即：AI将再次颠覆我们的认知', 'hot_value': 9800000},
    {'title': '英伟达新一代芯片性能曝光，算力翻倍', 'hot_value': 8900000},
    {'title': '苹果Vision Pro 2代即将发布，价格腰斩？', 'hot_value': 8500000},
    {'title': '特斯拉FSD入华倒计时，自动驾驶要变天', 'hot_value': 8200000},
    {'title': '华为纯血鸿蒙正式推送，告别安卓内核', 'hot_value': 7900000},
    {'title': 'DeepSeek新模型震撼发布，开源AI再突破', 'hot_value': 7600000},
    {'title': '小米汽车销量暴涨，造车新势力洗牌', 'hot_value': 7300000},
    {'title': 'OpenAI宣布重大更新，ChatGPT全面进化', 'hot_value': 7000000},
    {'title': '脑机接口人体试验成功，科幻照进现实', 'hot_value': 6800000},
    {'title': '折叠屏手机价格跌破3000元，普及时代来了', 'hot_value': 6500000},
    {'title': '量子计算机商用化加速，传统加密面临挑战', 'hot_value': 6200000},
    {'title': 'SpaceX星舰第四次试飞成功，火星更近了', 'hot_value': 5900000},
    {'title': 'Sora视频生成能力再升级，影视行业慌了', 'hot_value': 5600000},
    {'title': '国产大模型集体降价，AI应用迎来爆发期', 'hot_value': 5300000},
    {'title': '苹果AI战略曝光，Siri终于要变聪明了', 'hot_value': 5000000},
    {'title': '人形机器人开始进入工厂，替代人工不远了', 'hot_value': 4800000},
    {'title': '固态电池技术突破，电动车续航破1000公里', 'hot_value': 4500000},
    {'title': 'Kimi智能助手用户破亿，国产AI崛起', 'hot_value': 4200000},
    {'title': '6G研发提速，网速比5G快50倍不是梦', 'hot_value': 3900000},
    {'title': '数字人民币新功能上线，支付格局要变', 'hot_value': 3600000},
]

TECH_KEYWORDS = [
    'AI', 'GPT', 'ChatGPT', '机器人', '芯片', '半导体',
    '苹果', '华为', '小米', '特斯拉', '科技', '元宇宙',
    'VR', 'AR', '区块链', '量子', '5G', '6G', '新能源',
    '自动驾驶', '大模型', '算力', '英伟达', 'OpenAI', 'DeepSeek',
    '智能', '数字', '互联网', '算法', '数据', 'SpaceX',
]


def is_tech(title):
    t = title.lower()
    return any(k.lower() in t for k in TECH_KEYWORDS)


def get_viral_titles(base):
    templates = [
        f"\U0001f525 {base}\uff01\u8fd9\u6ce2\u64cd\u4f5c\u6211\u770b\u4edc\u4e86",
        f"\u8bf4\u771f\u7684\uff0c{base}\u53ef\u80fd\u6539\u53d8\u4e00\u5207",
        f"{base}\uff1a\u6211\u4f53\u9a8c\u5b8c\u53ea\u60f3\u8bf4\u4e00\u4e2a\u5b57",
        f"\u6df1\u5ea6\u4f53\u9a8c {base} \u540e\uff0c\u6211\u53d1\u73b0\u4e86\u4e00\u4e2a\u79d8\u5bc6...",
        f"\u522b\u518d\u88ab\u9a97\u4e86\uff01\u5173\u4e8e{base}\u7684\u771f\u76f8",
        f"\u521a\u8bd5\u4e86{base}\uff0c\u6211\u7684\u4e0b\u5df4\u6389\u4e0b\u6765\u4e86",
        f"\u4e3a\u4ec0\u4e48\u61c2\u7684\u4eba\u90fd\u5728\u804a{base}\uff1f",
        f"{base}\u6765\u4e86\uff01\u666e\u901a\u4eba\u600e\u4e48\u6293\u4f4f\u673a\u4f1a\uff1f",
        f"\u5b9e\u6d4b {base}\uff0c\u7ed3\u679c\u8ba9\u6211\u610f\u5916",
        f"\u5173\u4e8e{base}\uff099%\u7684\u4eba\u90fd\u4e0d\u77e5\u9053\u7684\u4e8b",
    ]
    random.shuffle(templates)
    return templates[:8]


def build_topics():
    """Build topic list - always returns data instantly."""
    now = datetime.now().isoformat()
    topics = []
    for item in FALLBACK_TOPICS:
        topics.append({
            **item,
            'source': 'built-in',
            'fetched_at': now,
            'url': '',
        })
    
    # Sort: tech first, then by hot value
    topics.sort(key=lambda x: (
        0 if is_tech(x.get('title', '')) else 1,
        -x.get('hot_value', 0)
    ))
    return topics[:50]


# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('dashboard.html', today_stats={}, history=[], wechat_configured=False)


@app.route('/topics')
def topics_page():
    """Serve the self-contained topics page (no template needed)."""
    try:
        with open(os.path.join(STATIC_DIR, 'topics.html'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return "Page not found", 404


@app.route('/editor')
def editor_page():
    """Serve the self-contained article editor."""
    try:
        with open(os.path.join(STATIC_DIR, 'editor.html'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except FileNotFoundError:
        return "Page not found", 404


@app.route('/api/article/generate', methods=['POST'])
def api_generate_article():
    """Generate an article from a topic + auto-generate images for key paragraphs."""
    try:
        data = request.get_json(force=True)
        topic = data.get('topic', '')
        title = data.get('title', topic)
        selected_title = data.get('selected_title', '')
        extra_context = data.get('extra_context', '')
        style = data.get('style', 'objective')
        auto_images = data.get('auto_images', True)  # default: auto-gen images

        if not topic:
            return jsonify({'success': False, 'error': '请选择一个话题'})

        sys.path.insert(0, BASE_DIR)
        from modules.article_generator import ArticleGenerator
        config = {
            'MIN_PARAGRAPHS': 5,
            'MAX_PARAGRAPHS': 8,
            'IMAGES_PER_ARTICLE': 4,  # 总配图上限（含封面）
            'ARTICLE_STYLE': style,
        }

        generator = ArticleGenerator(config)
        result = generator.generate(
            topic=topic,
            title=title,
            selected_title=selected_title or None,
            extra_context=extra_context,
            author_name='AI观察者',
            style=style,
        )

        # Clean up paragraphs for frontend display
        clean_paragraphs = []
        for idx, p in enumerate(result.get('paragraphs', [])):
            para_data = {
                'type': p.get('type', 'body'),
                'text': p.get('text', ''),
                'char_count': p.get('char_count', 0),
                'image_hint': p.get('image_hint', ''),
                'needs_image': p.get('needs_image', False),
                'highlights': p.get('highlights', []),
            }
            
            # Auto-generate image for this paragraph if enabled and has hint
            if auto_images and p.get('image_hint') and p.get('needs_image'):
                # Only auto-gen for opening (1st) and body paragraphs at key positions
                para_type = p.get('type', 'body')
                should_auto = (
                    para_type == 'opening' or  # always gen for opening
                    (para_type in ('body', 'ending') and idx in [1, len(result.get('paragraphs', [])) // 2])  # middle + near end
                )
                if should_auto:
                    img_url = _auto_gen_image_for_para(p.get('image_hint', ''), idx, topic)
                    if img_url:
                        para_data['hasImage'] = True
                        para_data['imageUrl'] = img_url

            clean_paragraphs.append(para_data)

        # Auto-generate cover image
        cover_img_url = None
        if auto_images:
            cover_hint = result.get('cover_image_hint', '') or f'{topic} 封面图'
            cover_img_url = _auto_gen_image_for_para(cover_hint, -1, topic)

        return jsonify({
            'success': True,
            'data': {
                'title': result.get('title', title),
                'original_topic': result.get('original_topic', topic),
                'author': result.get('author', 'AI观察者'),
                'style': result.get('style', ''),
                'paragraphs': clean_paragraphs,
                'word_count': result.get('word_count', 0),
                'created_at': result.get('created_at', ''),
                'tags': result.get('tags', []),
                'summary': result.get('summary', ''),
                'cover_image_hint': result.get('cover_image_hint', ''),
                'cover_image_url': cover_img_url,
            },
        })

    except Exception as e:
        log.error(f"Article generation error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'生成失败: {str(e)}'})


def _auto_gen_image_for_para(prompt: str, index: int, topic: str) -> str:
    """Auto-generate an image for a paragraph. Returns URL or None on failure."""
    try:
        import os
        import hashlib
        
        output_dir = os.path.join(BASE_DIR, 'static', 'generated_images')
        os.makedirs(output_dir, exist_ok=True)
        
        content_hash = hashlib.md5(f"{prompt}_{index}".encode()).hexdigest()[:12]
        img_filename = f"img_{content_hash}_{index}.png"
        img_path = os.path.join(output_dir, img_filename)
        
        if os.path.exists(img_path) and os.path.getsize(img_path) > 1000:
            return f'/static/generated_images/{img_filename}'
        
        sys.path.insert(0, BASE_DIR)
        from tools.image_helper import generate_image
        full_prompt = f"{prompt}"
        result = generate_image(full_prompt, img_path, size="1080x1920")
        
        if result == "OK" and os.path.exists(img_path):
            return f'/static/generated_images/{img_filename}'
    except Exception as e:
        log.warning(f"Auto-image gen failed for para {index}: {e}")
    return None


@app.route('/api/article/styles', methods=['GET'])
def api_article_styles():
    """Return available writing styles."""
    from modules.article_generator import WRITING_STYLES
    return jsonify({'success': True, 'data': WRITING_STYLES})


@app.route('/api/image/generate', methods=['POST'])
def api_generate_image():
    """Generate AI image for a paragraph - direct call, no subprocess."""
    try:
        data = request.get_json(force=True)
        prompt = data.get('prompt', '')
        index = data.get('index', 0)
        topic = data.get('topic', '')

        if not prompt:
            return jsonify({'success': False, 'error': '缺少图片描述'})

        import os

        output_dir = os.path.join(BASE_DIR, 'static', 'generated_images')
        os.makedirs(output_dir, exist_ok=True)

        # Use deterministic filename based on content hash + index
        import hashlib
        content_hash = hashlib.md5(f"{prompt}_{index}".encode()).hexdigest()[:12]
        img_filename = f"img_{content_hash}_{index}.png"
        img_path = os.path.join(output_dir, img_filename)

        # If file already exists, return it directly
        if os.path.exists(img_path) and os.path.getsize(img_path) > 1000:
            url = f'/static/generated_images/{img_filename}'
            return jsonify({'success': True, 'data': {'url': url, 'path': img_path}})

        # Direct import and call - NO subprocess
        sys.path.insert(0, BASE_DIR)
        from tools.image_helper import generate_image
        full_prompt = f"{prompt}, vertical composition 9:16, modern tech style"
        result = generate_image(full_prompt, img_path, size="1080x1920")

        if result == "OK" and os.path.exists(img_path):
            url = f'/static/generated_images/{img_filename}'
            return jsonify({
                'success': True,
                'data': {'url': url, 'path': img_path}
            })
        else:
            log.error(f"Image generation failed: {result}")
            return jsonify({
                'success': False,
                'error': f'图片生成失败: {result}'
            })

    except Exception as e:
        log.error(f"Image generation error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': f'生成失败: {str(e)}'})


@app.route('/publish')
def publish_page():
    return render_template('publish.html', stats={}, history=[], wechat_configured=False)


@app.route('/settings')
def settings_page():
    return render_template('settings.html', configured=False, appid='', secret='')


@app.route('/api/topics/fetch')
def api_fetch_topics():
    """Fetch topics: tries real network first, falls back instantly."""
    try:
        raw = []
        
        # Try real fetch from network (with short timeout)
        try:
            sys.path.insert(0, BASE_DIR)
            from modules.hot_topics import HotTopicFetcher
            config = {'HOT_SOURCES': [
                {'name': '今日头条', 'enabled': True},
                {'name': '百度热搜', 'enabled': True},
                {'name': 'Tophub微博', 'enabled': True},
            ]}
            fetcher = HotTopicFetcher(config)
            raw = fetcher.fetch_all()
        except Exception as net_err:
            log.warning(f"Network fetch failed, using fallback: {net_err}")
            raw = []  # will trigger fallback below

        # If network returned nothing, use built-in fallback
        if not raw:
            now = datetime.now().isoformat()
            for item in FALLBACK_TOPICS:
                raw.append({
                    **item,
                    'source': 'built-in-fallback',
                    'fetched_at': now,
                    'url': '',
                })

        # Build response
        result = []
        for t in raw[:20]:
            result.append({
                'title': t.get('title', ''),
                'hot_value': t.get('hot_value', 0),
                'source': t.get('source', ''),
                'category': t.get('category', ''),
                'url': t.get('url', ''),
                'viral_titles': get_viral_titles(t.get('title', '')),
                'is_tech': is_tech(t.get('title', '')),
                'fetched_at': t.get('fetched_at', ''),
            })

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        log.error(f"Topics error: {e}")
        return jsonify({
            'success': True,
            'data': [{
                'title': '\u6df1\u5ea6\u4f53\u9a8c GPT-5...',
                'hot_value': 9990000,
                'source': 'fallback',
                'viral_titles': ['GPT-5\u6765\u4e86'],
                'is_tech': True,
            }]
        })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'not found'}), 404


if __name__ == '__main__':
    print("=" * 50)
    print("  WeChat Publisher Server")
    print("  http://127.0.0.1:8080")
    print("=" * 50)
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)
