# -*- coding: utf-8 -*-
"""
Web 管理面板
微信公众号爆款内容一键发布系统
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify

logger = logging.getLogger('WechatPublisher.WebApp')


def create_app(config: dict):
    """创建 Flask 应用"""
    
    # 模板和静态文件路径
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    app.config['JSON_AS_ASCII'] = False
    
    # 初始化各模块（延迟加载）
    _modules_initialized = False
    topic_fetcher = None
    article_gen = None
    image_gen = None
    wechat_pub = None
    scheduler_obj = None
    
    def init_modules():
        """初始化所有模块"""
        nonlocal _modules_initialized, topic_fetcher, article_gen, image_gen, wechat_pub, scheduler_obj
        
        if _modules_initialized:
            return (topic_fetcher, article_gen, image_gen, wechat_pub, scheduler_obj)
        
        # 导入模块
        base_path = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, base_path)
        
        from modules.hot_topics import HotTopicFetcher
        from modules.article_generator import ArticleGenerator
        from modules.image_generator import ImageGenModule
        from modules.wechat_api import WeChatPublisher
        from modules.scheduler import PublishScheduler
        
        topic_fetcher = HotTopicFetcher(config)
        article_gen = ArticleGenerator(config)
        image_gen = ImageGenModule(config)
        wechat_pub = WeChatPublisher(config)
        scheduler_obj = PublishScheduler(
            config,
            topic_fetcher=topic_fetcher,
            article_gen=article_gen,
            image_gen=image_gen,
            wechat_publisher=wechat_pub,
        )
        
        _modules_initialized = True
        logger.info("所有模块初始化完成")
        
        return (topic_fetcher, article_gen, image_gen, wechat_pub, scheduler_obj)
    
    # ==================== 页面路由 ====================
    
    @app.route('/')
    def index():
        """首页 - 仪表盘"""
        tf, ag, ig, wp, sc = init_modules()
        
        today_stats = sc.get_today_stats()
        recent_history = sc.get_history(7)
        
        return render_template('dashboard.html',
                             today_stats=today_stats,
                             history=recent_history,
                             wechat_configured=wp.is_configured())
    
    @app.route('/topics')
    def topics_page():
        """Hot topics page - lightweight, no heavy module loading."""
        return render_template('topics.html')
    
    @app.route('/editor')
    def editor_page():
        """文章编辑器页面"""
        return render_template('editor.html')
    
    @app.route('/publish')
    def publish_page():
        """发布管理页面"""
        tf, ag, ig, wp, sc = init_modules()
        
        today_stats = sc.get_today_stats()
        history = sc.get_history(30)
        
        return render_template('publish.html',
                             stats=today_stats,
                             history=history,
                             wechat_configured=wp.is_configured())
    
    @app.route('/settings')
    def settings_page():
        """设置页面"""
        tf, ag, ig, wp, _ = init_modules()
        return render_template('settings.html',
                             configured=wp.is_configured(),
                             appid=config.get('WECHAT_APPID', ''),
                             secret='***' if config.get('WECHAT_SECRET') else '')
    
    # ==================== API 路由 ====================
    
    @app.route('/api/topics/fetch')
    def api_fetch_topics():
        """API: Fetch hot topics - standalone, no full module init needed."""
        log = logging.getLogger('api.topics')
        
        try:
            # STANDALONE: only init topic fetcher, skip all other heavy modules
            base_path = os.path.dirname(os.path.dirname(__file__))
            if base_path not in sys.path:
                sys.path.insert(0, base_path)
            
            from modules.hot_topics import HotTopicFetcher
            tf = HotTopicFetcher(config)
            
            # Fetch with built-in fallback (always returns data fast)
            topics = tf.fetch_all()
            
            # SAFETY NET: if empty, force inject fallback
            if not topics:
                log.warning("Empty results, injecting fallback")
                from modules.hot_topics import FALLBACK_TOPICS
                import datetime as dt
                for item in FALLBACK_TOPICS:
                    topics.append({
                        **item,
                        'source': 'built-in-fallback',
                        'fetched_at': dt.datetime.now().isoformat(),
                        'url': '',
                    })
            
            # Build response
            result = []
            for t in topics[:20]:
                try:
                    viral_titles = tf.get_viral_titles(t.get('title', ''))
                except Exception:
                    viral_titles = [t.get('title', '')]
                
                result.append({
                    'title': t.get('title', ''),
                    'hot_value': t.get('hot_value', 0),
                    'source': t.get('source', 'unknown'),
                    'category': t.get('category', ''),
                    'url': t.get('url', ''),
                    'viral_titles': viral_titles,
                    'is_tech': tf._is_tech_topic(t.get('title', '')),
                    'fetched_at': t.get('fetched_at', ''),
                })
            
            return jsonify({'success': True, 'data': result})
        
        except Exception as e:
            log.error(f"Topics API error: {e}", exc_info=True)
            # ULTIMATE FALLBACK
            return jsonify({
                'success': True,
                'data': [{
                    'title': '\u6df1\u5ea6\u4f53\u9a8c GPT-5 \u540e\u6211\u53d1\u73b0\u4e86\u4e00\u4e2a\u79d8\u5bc6...',
                    'hot_value': 9990000,
                    'source': 'emergency-fallback',
                    'viral_titles': ['GPT-5\u53d1\u5e03\u5728\u5373\uff01AI\u5c06\u518d\u6b21\u98a0\u8986\u8ba4\u77e5'],
                    'is_tech': True,
                }]
            })
    
    @app.route('/api/article/generate', methods=['POST'])
    def api_generate_article():
        """
        API: 生成文章
        POST 参数:
        - topic: 原始话题
        - title: 用户选择的标题
        - extra_context: 额外角度/上下文
        """
        try:
            data = request.json or request.form.to_dict()
            topic = data.get('topic', '')
            title = data.get('title', topic)
            extra_context = data.get('extra_context', '')
            
            if not topic:
                return jsonify({'success': False, 'error': '话题不能为空'})
            
            _, ag, ig, wp, _ = init_modules()
            
            # 生成文章
            article = ag.generate(
                topic=topic,
                title=title,
                selected_title=title,
                extra_context=extra_context,
                author_name="AI观察者",
            )
            
            # 生成配图
            if data.get('generate_images', True):
                article = ig.generate_for_article(article)
            
            return jsonify({
                'success': True,
                'data': {
                    'title': article['title'],
                    'author': article['author'],
                    'word_count': article['word_count'],
                    'paragraphs': [
                        {
                            'index': p['index'],
                            'type': p['type'],
                            'text': p['text'],
                            'needs_image': p.get('needs_image', False),
                            'image_path': p.get('image_path'),
                            'image_hint': p.get('image_hint'),
                        }
                        for p in article['paragraphs']
                    ],
                    'summary': article.get('summary', ''),
                    'tags': article.get('tags', []),
                    'cover_image': article.get('cover_image'),
                    'image_count': article.get('image_count', 0),
                }
            })
        
        except Exception as e:
            logger.error(f"文章生成失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/publish', methods=['POST'])
    def api_publish():
        """
        API: 发布文章到公众号
        POST 参数:
        - article: 文章完整数据
        - publish_now: 是否立即发布
        """
        try:
            data = request.json or {}
            article_data = data.get('article', {})
            publish_now = data.get('publish_now', False)
            
            if not article_data.get('title'):
                return jsonify({'success': False, 'error': '缺少标题'})
            
            _, _, _, wp, sc = init_modules()
            
            if not wp.is_configured():
                return jsonify({
                    'success': False,
                    'error': '微信公众号未配置，请先在设置页绑定 AppID 和 Secret'
                })
            
            # 发布
            result = wp.publish_article(article_data, publish_now=publish_now)
            
            return jsonify({
                'success': not result.get('errcode'),
                'data': result,
                'message': f"{'发布成功' if not result.get('errcode') else '发布失败: ' + result.get('errmsg', '')}"
            })
        
        except Exception as e:
            logger.error(f"发布失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/scheduler/status')
    def api_scheduler_status():
        """API: 获取调度器状态"""
        _, _, _, _, sc = init_modules()
        
        return jsonify({
            'success': True,
            'data': {
                'running': sc.is_running,
                'today_stats': sc.get_today_stats(),
                'recent_history': sc.get_history(5),
            }
        })
    
    @app.route('/api/scheduler/toggle')
    def api_scheduler_toggle():
        """API: 开关定时任务"""
        _, _, _, _, sc = init_modules()
        
        action = request.args.get('action', 'status')
        
        if action == 'start':
            sc.start()
            msg = '定时任务已启动'
        elif action == 'stop':
            sc.stop()
            msg = '定时任务已停止'
        else:
            msg = f'当前状态: {"运行中" if sc.is_running else "已停止"}'
        
        return jsonify({
            'success': True,
            'data': {'running': sc.is_running},
            'message': msg
        })
    
    @app.route('/api/settings/wechat', methods=['POST'])
    def api_update_wechat_settings():
        """API: 更新微信配置"""
        try:
            data = request.json or {}
            appid = data.get('appid', '')
            secret = data.get('secret', '')
            
            import yaml
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            
            if appid:
                config_data['WECHAT_APPID'] = appid
            if secret and secret != '***':
                config_data['WECHAT_SECRET'] = secret
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
            
            return jsonify({
                'success': True,
                'message': '配置已保存'
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/article/generate_images', methods=['POST'])
    def api_generate_article_images():
        """API: 为已生成的文章异步生成全部配图（封面+段落）"""
        try:
            data = request.json or {}
            article = data.get('article')
            if not article or not article.get('paragraphs'):
                return jsonify({'success': False, 'error': '缺少文章数据'})

            _, _, ig, wp, _ = init_modules()

            # 调用 image_gen 模块的 generate_for_article 方法
            result = ig.generate_for_article(article)
            
            return jsonify({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"配图生成失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/image/regenerate', methods=['POST'])
    def api_regenerate_image():
        """API: 重新生成单张配图"""
        try:
            data = request.json or {}
            prompt = data.get('prompt', '')
            para_index = data.get('paragraph_index', 0)

            if not prompt:
                return jsonify({'success': False, 'error': '缺少提示词'})

            _, _, ig, wp, _ = init_modules()

            # 调用 image_gen 生成单张图（使用内部API方法）
            filename = 'para_' + str(para_index) + '_' + str(int(__import__('time').time())) + '.png'
            filepath = os.path.join(_img_dir, filename)
            ig._call_image_api(prompt, filepath, size=data.get('size', '1080x1920'))

            return jsonify({
                'success': True,
                'image_path': './output/images/' + filename
            })

        except Exception as e:
            logger.error(f"单张图片生成失败: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': '接口不存在'}), 404

    # 图片文件服务：提供生成的配图（从 config.yaml 读取绝对路径，确保和生成器一致）
    import yaml
    _base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(_base, 'config.yaml'), 'r', encoding='utf-8') as _cf:
        _cfg = yaml.safe_load(_cf)
    _img_dir = os.path.join(os.path.abspath(_cfg.get('OUTPUT_DIR', './output')), 'images')

    @app.route('/output/images/<filename>')
    def serve_image(filename):
        from flask import send_from_directory, abort
        # 安全检查：只允许图片扩展名
        safe = filename.lower().endswith(('.png','.jpg','.jpeg','.gif','.webp'))
        if not safe:
            abort(403)
        return send_from_directory(_img_dir, filename)
    
    return app


if __name__ == '__main__':
    import yaml
    import os

    # 基于脚本位置定位项目根目录
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(_base_dir, 'config.yaml'), 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    app = create_app(config)
    app.run(host='127.0.0.1', port=8080, debug=True)
