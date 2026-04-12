# -*- coding: utf-8 -*-
"""
微信公众号爆款内容自动生成 + 发布系统
一键发布 Web 面板

功能：
1. 热门话题抓取（微博/百度热搜）
2. AI 文章生成（人称叙述 + 娱乐性）
3. AI 配图生成（每段插入科技风图片）
4. 微信公众号 API 发布
5. 定时自动发布任务
"""

import os
import sys
import yaml
import logging
from datetime import datetime

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载配置
def load_config():
    config_path = os.path.join(BASE_DIR, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# 日志配置
log_dir = os.path.join(BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(
            os.path.join(log_dir, f'publisher_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        ),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('WechatPublisher')


# ============================================================
# 导入各模块
# ============================================================
from modules.hot_topics import HotTopicFetcher
from modules.article_generator import ArticleGenerator
from modules.image_generator import ImageGenModule
from modules.wechat_api import WeChatPublisher
from modules.scheduler import PublishScheduler


def main():
    """主入口 - 启动 Web 管理面板"""
    logger.info("=" * 50)
    logger.info("微信公众号爆款内容发布系统启动")
    logger.info("=" * 50)
    
    from web.app import create_app
    app = create_app(CONFIG)
    
    host = CONFIG.get('WEB_HOST', '127.0.0.1')
    port = CONFIG.get('WEB_PORT', 8080)
    
    logger.info(f"Web 面板地址: http://{host}:{port}")
    app.run(host=host, port=port, debug=CONFIG.get('WEB_DEBUG', True))


if __name__ == '__main__':
    main()
