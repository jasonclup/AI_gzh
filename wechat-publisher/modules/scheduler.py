# -*- coding: utf-8 -*-
"""
定时发布任务调度器
- 每天自动抓取热点
- 自动生成 1-3 篇文章
- 自动发布到公众号
"""

import os
import json
import logging
import threading
import random
import schedule as scheduler
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger('WechatPublisher.PublishScheduler')


class PublishScheduler:
    """定时发布任务调度器"""
    
    def __init__(self, config: dict, 
                 topic_fetcher=None,
                 article_gen=None,
                 image_gen=None,
                 wechat_publisher=None):
        self.config = config
        self.topic_fetcher = topic_fetcher
        self.article_gen = article_gen
        self.image_gen = image_gen
        self.wechat_pub = wechat_publisher
        
        self.is_running = False
        self._thread = None
        
        # 发布时间配置（每天1篇，随机偏移避免机器人特征）
        self.publish_times = [
            "09:00",   # 日间发布（唯一时段，会加随机偏移）
        ]
        
        # 任务历史记录
        self.history_file = os.path.join(
            config.get('OUTPUT_DIR', './output'),
            'publish_history.json'
        )
        self._load_history()
    
    def start(self):
        """启动定时调度器"""
        if self.is_running:
            logger.warning("调度器已在运行")
            return
        
        # 注册定时任务
        for time_slot in self.publish_times:
            scheduler.every().day.at(time_slot).do(
                self._scheduled_publish, time_slot=time_slot
            )
            logger.info(f"已注册定时任务: 每天 {time_slot}")
        
        # 启动后台线程
        self.is_running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        logger.info("定时发布调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.is_running = False
        scheduler.clear()
        logger.info("定时发布调度器已停止")
    
    def _run_loop(self):
        """运行调度循环"""
        while self.is_running:
            scheduler.run_pending()
            sleep_seconds = min(60, max(1, 60))  # 每分钟检查一次
            
            import time
            time.sleep(sleep_seconds)
    
    def _scheduled_publish(self, time_slot: str):
        """
        定时发布执行逻辑
        1. 抓取今日热门话题
        2. 选择话题生成文章
        3. 生成配图
        4. 发布到公众号
        
        安全机制: 每次执行时增加0-90分钟随机偏移，避免固定时间发布被识别为机器人
        """
        # 随机偏移 (0-90分钟)，模拟真人发文时间的不确定性
        random_delay = random.randint(0, 5400)  # 最多90分钟
        logger.info(f"定时任务 [{time_slot}] 触发，将在 {random_delay//60}分{random_delay%60}秒 后执行（反检测随机偏移）")
        
        import time
        time.sleep(random_delay)
        
        logger.info(f"===== 开始定时发布任务 [{time_slot}] =====")
        
        try:
            # 1. 获取热门话题
            topics = self.topic_fetcher.fetch_all() if self.topic_fetcher else []
            
            if not topics:
                logger.warning("未获取到任何热门话题，跳过本次发布")
                return
            
            # 过滤掉今天已经发过的主题
            today_published = [h.get('topic', '') for h in self.history 
                              if h.get('date') == datetime.now().strftime('%Y-%m-%d')]
            
            available_topics = [t for t in topics 
                               if t.get('title', '') not in today_published]
            
            if not available_topics:
                logger.info("今日热门话题已全部发布过，跳过")
                return
            
            # 2. 随机选择话题（优先科技类）
            selected_topic = available_topics[0]
            
            # 3. 生成爆款标题变体供选择（自动选第一个）
            viral_titles = self.topic_fetcher.get_viral_titles(selected_topic['title'])
            selected_title = viral_titles[0]
            
            # 4. 生成文章
            if self.article_gen:
                article = self.article_gen.generate(
                    topic=selected_topic['title'],
                    title=selected_topic['title'],
                    selected_title=selected_title,
                    author_name="往前看的月半子"
                )
                
                # 5. 生成配图
                if self.image_gen:
                    article = self.image_gen.generate_for_article(article)
                
                # 6. 发布
                result = None
                if self.wechat_pub and self.wechat_pub.is_configured():
                    try:
                        result = self.wechat_pub.publish_article(article)
                    except Exception as e:
                        logger.error(f"发布失败: {e}")
                        result = {"error": str(e)}
                
                # 记录历史
                record = {
                    'time': datetime.now().isoformat(),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time_slot': time_slot,
                    'topic': selected_topic['title'],
                    'title': article.get('title', ''),
                    'source': selected_topic.get('source', ''),
                    'status': 'success' if result and not result.get('error') else 'failed',
                    'publish_result': str(result) if result else 'skipped',
                    'article_word_count': article.get('word_count', 0),
                    'image_count': article.get('image_count', 0),
                }
                
                self._add_to_history(record)
                logger.info(f"定时发布完成: {article.get('title', '')} | "
                           f"{record['status']} | {article.get('word_count', 0)}字")
            
        except Exception as e:
            logger.error(f"定时发布任务异常: {e}", exc_info=True)
        
        logger.info(f"===== 定时发布任务结束 [{time_slot}] =====")
    
    def manual_publish(self, topic: str, title: str = None) -> Dict:
        """
        手动触发一次发布
        用于 Web 面板的"立即发布"按钮
        """
        if not self.article_gen:
            return {'error': '文章生成器未初始化'}
        
        logger.info(f"[手动发布] 主题: {topic}, 标题: {title or '自动生成'}")
        
        # 生成文章
        article = self.article_gen.generate(
            topic=topic,
            title=title or topic,
            author_name="往前看的月半子"
        )
        
        # 生成配图
        if self.image_gen:
            article = self.image_gen.generate_for_article(article)
        
        # 发布
        publish_result = None
        if self.wechat_pub:
            try:
                publish_result = self.wechat_pub.publish_article(article)
            except Exception as e:
                publish_result = {'error': str(e)}
        
        # 记录
        record = {
            'time': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time_slot': 'manual',
            'topic': topic,
            'title': article.get('title', ''),
            'status': 'success' if publish_result and not publish_result.get('error') else 'failed',
            'publish_result': str(publish_result),
            'article_word_count': article.get('word_count', 0),
        }
        self._add_to_history(record)
        
        return {
            'article': article,
            'publish_result': publish_result,
            'record': record
        }
    
    def get_today_stats(self) -> Dict:
        """获取今日发布统计"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_records = [h for h in self.history if h.get('date') == today]
        
        return {
            'today_count': len(today_records),
            'target_min': self.config.get('DAILY_ARTICLE_COUNT', [1, 3])[0],
            'target_max': self.config.get('DAILY_ARTICLE_COUNT', [1, 3])[1],
            'success_count': sum(1 for r in today_records if r.get('status') == 'success'),
            'records': today_records[-5:],  # 最近5条
        }
    
    def get_history(self, days: int = 7) -> List[Dict]:
        """获取最近N天的历史记录"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return [h for h in self.history if h.get('date', '') >= cutoff]
    
    # ==================== 历史记录管理 ====================
    
    def _load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                logger.warning(f"加载历史记录失败: {e}")
                self.history = []
        else:
            self.history = []
    
    def _add_to_history(self, record: dict):
        """添加一条历史记录"""
        self.history.append(record)
        
        # 只保留最近90天
        cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        self.history = [h for h in self.history if h.get('date', '') >= cutoff]
        
        # 保存
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    print("PublishScheduler - 定时发布调度器")
    print("\n使用方式:")
    print("  scheduler.start()   # 启动定时任务")
    print("  scheduler.stop()    # 停止定时任务")
    print("  scheduler.manual_publish('话题')  # 手动发布")
