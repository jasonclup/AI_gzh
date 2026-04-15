# -*- coding: utf-8 -*-
"""
文章数据回流系统 ArticlePerformanceTracker v1.0
记录每篇已发表文章的阅读/点赞/分享数据，
形成正向飞轮——知道什么有效、什么无效
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# 配置常量
# ============================================================

DATA_DIR = Path(__file__).parent / "output" / "performance"
PERFORMANCE_FILE = DATA_DIR / "article_performance.json"
WEEKLY_REPORT_DIR = DATA_DIR / "weekly_reports"

# 数据字段定义
REQUIRED_FIELDS = ['article_title', 'publish_date', 'topic', 'title_template']
OPTIONAL_FIELDS = [
    'read_count', 'like_count', 'share_count', 'comment_count',
    'finish_rate',  # 完读率（如果微信后台能拿到）
    'word_count',
    'image_count',
    'category',     # 文章分类(tech_viral/life_share等)
    'tags',         # 标签列表
    'score_before_publish',  # 发表前选题评分
    'alt_titles',   # 备选标题列表
    'chosen_title_index',    # 最终选择的标题索引（用于A/B测试）
    'notes',        # 手动备注
]

# 表现等级阈值
PERFORMANCE_TIERS = {
    'S': {'min_read': 10000, 'label': '爆款'},
    'A': {'min_read': 5000, 'label': '优秀'},
    'B': {'min_read': 2000, 'label': '良好'},
    'C': {'min_read': 500, 'label': '一般'},
    'D': {'min_read': 0, 'label': '低迷'},
}


# ============================================================
# 核心类
# ============================================================

class ArticlePerformanceTracker:
    """文章表现追踪器"""

    def __init__(self):
        self.data_file = PERFORMANCE_FILE
        self.articles = self._load_data()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_data(self):
        """加载已有数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_data(self):
        """保存数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)

    # ---- 核心操作 ----

    def record_article(self, article_data):
        """
        记录一篇新文章（发表时调用）
        
        Args:
            article_data: dict，至少包含：
                - article_title: str
                - publish_date: str (YYYY-MM-DD)
                - topic: str (热点话题)
                - title_template: str (使用的标题模板类型)
        
        Returns:
            dict: 记录结果
        """
        # 验证必填字段
        for field in REQUIRED_FIELDS:
            if field not in article_data:
                raise ValueError(f"缺少必填字段: {field}")
        
        record = {
            'id': len(self.articles) + 1,
            'recorded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            **{k: v for k, v in article_data.items() if k in REQUIRED_FIELDS + OPTIONAL_FIELDS},
            'performance_tier': None,  # 等待数据更新后计算
            'engagement_rate': None,
            'data_updated_at': None,
        }
        
        self.articles.append(record)
        self._save_data()
        
        return {
            'success': True,
            'article_id': record['id'],
            'message': f'文章已记录: {article_data["article_title"][:30]}'
        }

    def update_performance(self, article_id_or_title, performance_data):
        """
        更新文章的表现数据
        
        Args:
            article_id_or_title: int 或 str（文章ID或标题关键词）
            performance_data: dict，包含：
                - read_count: int
                - like_count: int (可选)
                - share_count: int (可选)
                - comment_count: int (可选)
        
        Returns:
            dict: 更新结果
        """
        article = self._find_article(article_id_or_title)
        if not article:
            return {'success': False, 'message': f'未找到文章: {article_id_or_title}'}
        
        # 更新数据
        article['read_count'] = performance_data.get('read_count', article.get('read_count'))
        article['like_count'] = performance_data.get('like_count', article.get('like_count', ))
        article['share_count'] = performance_data.get('share_count', article.get('share_count', 0))
        article['comment_count'] = performance_data.get('comment_count', article.get('comment_count', 0))
        article['finish_rate'] = performance_data.get('finish_rate', article.get('finish_rate'))
        article['data_updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算互动率
        reads = max(article['read_count'] or 1, 1)
        likes = article.get('like_count') or 0
        shares = article.get('share_count') or 0
        comments = article.get('comment_count') or 0
        article['engagement_rate'] = round((likes + shares * 3 + comments * 2) / reads * 100, 2)
        
        # 计算表现等级
        article['performance_tier'] = self._calc_tier(article)
        
        self._save_data()
        
        return {
            'success': True,
            'article_id': article['id'],
            'tier': article['performance_tier'],
            'engagement_rate': article['engagement_rate'],
            'message': f'已更新: {article["article_title"][:30]} -> [{article["performance_tier"]}级]',
        }

    def batch_update_from_manual_input(self, updates_list):
        """
        批量手动录入数据（适用于每天手动查看后台后批量更新）
        
        Args:
            updates_list: list of dict，每个包含：
                - title_keyword: str (标题关键词用于匹配)
                - read_count: int
                - like_count: int (可选)
                - share_count: int (可选)
        """
        results = []
        for update in updates_list:
            keyword = update.pop('title_keyword')
            result = self.update_performance(keyword, update)
            results.append(result)
        return results

    # ---- 分析方法 ----

    def get_top_performers(self, n=5, days=30):
        """获取近期Top N最佳表现文章"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent = [a for a in self.articles 
                  if a.get('publish_date', '') >= cutoff and a.get('read_count')]
        
        recent.sort(key=lambda x: x.get('read_count', 0), reverse=True)
        return recent[:n]

    def get_worst_performers(self, n=3, days=30):
        """获取近期表现最差文章（用于反面学习）"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent = [a for a in self.articles 
                  if a.get('publish_date', '') >= cutoff and a.get('read_count')]
        
        recent.sort(key=lambda x: x.get('read_count', 0))
        return recent[:n]

    def analyze_patterns(self):
        """
        分析表现模式 — 找出什么有效、什么无效
        
        Returns:
            dict: 分析报告
        """
        with_data = [a for a in self.articles if a.get('read_count')]
        
        if len(with_data) < 3:
            return {
                'status': 'insufficient_data',
                'message': f'需要至少3篇有阅读数据的文章才能分析（当前{len(with_data)}篇）',
            }
        
        avg_reads = sum(a['read_count'] for a in with_data) / len(with_data)
        top_threshold = avg_reads * 2
        
        # 高表现 vs 低表现文章分组
        high_perf = [a for a in with_data if a['read_count'] >= top_threshold]
        low_perf = [a for a in with_data if a['read_count'] < avg_reads * 0.5]
        
        # 分析标题模板分布
        template_stats = {}
        for a in with_data:
            tmpl = a.get('title_template', 'unknown')
            if tmpl not in template_stats:
                template_stats[tmpl] = {'count': 0, 'total_reads': 0}
            template_stats[tmpl]['count'] += 1
            template_stats[tmpl]['total_reads'] += a['read_count']
        
        for tmpl in template_stats:
            stats = template_stats[tmpl]
            stats['avg_reads'] = round(stats['total_reads'] / stats['count'])
        
        # 按平均阅读排序模板
        sorted_templates = sorted(template_stats.items(), key=lambda x: x[1]['avg_reads'], reverse=True)
        
        # 分析分类效果
        category_stats = {}
        for a in with_data:
            cat = a.get('category', 'unknown')
            if cat not in category_stats:
                category_stats[cat] = {'count': 0, 'total_reads': 0}
            category_stats[cat]['count'] += 1
            category_stats[cat]['total_reads'] += a['read_count']
        
        for cat in category_stats:
            s = category_stats[cat]
            s['avg_reads'] = round(s['total_reads'] / s['count'])
        
        sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['avg_reads'], reverse=True)
        
        # 最佳发布时段分析（如果有时间戳）
        hour_stats = {}
        for a in with_data:
            date_str = a.get('publish_date', '')
            hour = '未知'
            if date_str and len(date_str) >= 10:
                # 假设格式 YYYY-MM-DD HH:mm 或类似
                parts = date_str.replace('-', ' ').split()
                if len(parts) >= 2 and ':' in parts[1]:
                    try:
                        hour = parts[1].split(':')[0] + '点'
                    except:
                        pass
            
            if hour not in hour_stats:
                hour_stats[hour] = {'count': 0, 'total_reads': 0}
            hour_stats[hour]['count'] += 1
            hour_stats[hour]['total_reads'] += a['read_count']
        
        report = {
            'status': 'ok',
            'summary': {
                'total_articles_with_data': len(with_data),
                'avg_reads': round(avg_reads),
                'top_threshold': round(top_threshold),
                'high_perf_count': len(high_perf),
                'low_perf_count': len(low_perf),
            },
            'best_templates': [
                {'template': t, 'stats': s} for t, s in sorted_templates[:5]
            ],
            'worst_templates': [
                {'template': t, 'stats': s} for t, s in sorted_templates[-3:]
            ] if len(sorted_templates) > 3 else [],
            'best_categories': [
                {'category': c, 'stats': s} for c, s in sorted_categories[:5]
            ],
            'top_articles': [{
                'title': a['article_title'],
                'reads': a['read_count'],
                'tier': a['performance_tier'],
                'template': a.get('title_template'),
            } for a in self.get_top_performers(3)],
            'bottom_articles': [{
                'title': a['article_title'],
                'reads': a['read_count'],
                'tier': a['performance_tier'],
                'template': a.get('title_template'),
            } for a in self.get_worst_performers(3)],
            'recommendations': self._generate_recommendations(
                sorted_templates, sorted_categories, high_perf, low_perf
            ),
        }
        
        return report

    def generate_weekly_report(self):
        """
        生成本周数据报告并保存到文件
        """
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        
        analysis = self.analyze_patterns()
        
        report_lines = [
            f"# 公众号数据周报",
            f"",
            f"**周期**: {week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}",
            f"**生成时间**: {now.strftime('%Y-%m-%d %H:%M')}",
            f"",
        ]
        
        if analysis['status'] == 'insufficient_data':
            report_lines.append(f"> {analysis['message']}")
        else:
            summary = analysis['summary']
            report_lines.extend([
                f"## 总览",
                f"- 有数据文章数: **{summary['total_articles_with_data']}**篇",
                f"- 平均阅读: **{summary['avg_reads']}**",
                f"- 高表现线: >{summary['top_threshold']}阅读",
                f"- 爆款(S级): {analysis.get('top_articles', [])}篇",
                f"",
                f"## 标题模板排名（按平均阅读）",
            ])
            
            for item in analysis.get('best_templates', []):
                tmpl = item['template']
                s = item['stats']
                report_lines.append(f"- **{tmpl}**: {s['avg_reads']}阅读 ({s['count']}篇)")
            
            report_lines.extend([
                f"",
                f"## 分类效果排名",
            ])
            
            for item in analysis.get('best_categories', []):
                cat = item['category']
                s = item['stats']
                report_lines.append(f"- **{cat}**: {s['avg_reads']}阅读 ({s['count']}篇)")
            
            report_lines.extend([
                f"",
                f"## 优化建议",
            ])
            
            for rec in analysis.get('recommendations', []):
                report_lines.append(f"- {rec}")
        
        report_text = '\n'.join(report_lines)
        
        # 保存文件
        WEEKLY_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{now.strftime('%Y-W%W')}_report.md"
        filepath = WEEKLY_REPORT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return {
            'report_path': str(filepath),
            'report_text': report_text,
            'analysis': analysis,
        }

    # ---- 内部方法 ----

    def _find_article(self, id_or_title):
        """查找文章"""
        if isinstance(id_or_title, int):
            for a in self.articles:
                if a['id'] == id_or_title:
                    return a
            return None
        else:
            # 模糊匹配标题
            keyword = str(id_or_title).lower()
            matches = [a for a in self.articles if keyword in a.get('article_title', '').lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                # 多个匹配，返回最近的
                return max(matches, key=lambda a: a.get('id', 0))
            return None

    @staticmethod
    def _calc_tier(article):
        """计算表现等级"""
        reads = article.get('read_count') or 0
        engagement = article.get('engagement_rate') or 0
        
        for tier_name, tier_info in PERFORMANCE_TIERS.items():
            if reads >= tier_info['min_read']:
                continue  # 继续检查更高档位
        
        # 反向遍历找到合适的档次
        prev_min = 0
        for tier_name, tier_info in reversed(list(PERFORMANCE_TIERS.items())):
            if reads >= tier_info['min_read']:
                # 如果互动率高，升一档
                if engagement >= 8 and tier_name != 'S':
                    tier_order = list(PERFORMANCE_TIERS.keys())
                    idx = tier_order.index(tier_name)
                    if idx > 0:
                        return tier_order[idx - 1]
                return tier_name
        
        return 'D'

    def _generate_recommendations(self, templates, categories, high, low):
        """生成优化建议"""
        recs = []
        
        # 从高表现文章提取特征
        if templates:
            best_tmpl = templates[0][0] if templates else None
            worst_tmpl = templates[-1][0] if templates and len(templates) > 1 else None
            if best_tmpl and worst_tmpl and best_tmpl != worst_tmpl:
                recs.append(f'标题模板: "{best_tmpl}"表现最好，优先使用；谨慎使用"{worst_tmpl}"')
        
        if categories:
            best_cat = categories[0][0] if categories else None
            if best_cat:
                recs.append(f'内容分类: "{best_cat}"类文章平均阅读最高，可增加该类产出比例')
        
        if high:
            # 提取高表现文章的共同特征
            high_templates = set(a.get('title_template', '') for a in high)
            if len(high_templates) == 1:
                tmpl = list(high_templates)[0]
                recs.append(f'所有爆文都使用了"{tmpl}"模板，建议强化此方向')
        
        if low:
            recs.append(f'注意避免低表现文章的选题方向和标题模式')
        
        if not recs:
            recs.append('继续积累数据，积累更多文章后可进行更精准的分析')
        
        return recs

    # ---- 导出方法 ----

    def export_json(self, output_path=None):
        """导出完整数据为JSON"""
        path = output_path or (DATA_DIR / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_records': len(self.articles),
                'records': self.articles,
            }, f, ensure_ascii=False, indent=2)
        return str(path)

    def get_summary(self):
        """获取简要统计"""
        total = len(self.articles)
        with_data = sum(1 for a in self.articles if a.get('read_count'))
        total_reads = sum(a.get('read_count', 0) for a in self.articles)
        
        tiers = {}
        for a in self.articles:
            t = a.get('performance_tier', '-')
            tiers[t] = tiers.get(t, 0) + 1
        
        return {
            'total_articles': total,
            'with_data': with_data,
            'without_data': total - with_data,
            'total_reads': total_reads,
            'avg_reads': round(total_reads / max(with_data, 1)),
            'tier_distribution': tiers,
        }


# ============================================================
# 测试入口
# ============================================================

if __name__ == '__main__':
    tracker = ArticlePerformanceTracker()
    
    print("=" * 60)
    print("  文章数据回流测试")
    print("=" * 60)
    
    # 模拟记录几篇文章
    test_articles = [
        {
            'article_title': '姚安娜代言华为这事儿，我看完只说一句',
            'publish_date': '2026-04-15',
            'topic': '姚安娜代言华为Pura X Max',
            'title_template': '悬念式',
            'word_count': 1023,
            'image_count': 4,
            'category': 'tech_viral',
            'tags': ['华为', '代言', '手机'],
            'score_before_publish': 82,
            'alt_titles': [
                '姚安娜代言华为这事儿，我看完只说一句',
                '华为找姚安娜代言？我仔细看了三遍发布会',
                '华为Pura X Max发布：姚安娜代言背后的故事',
            ],
            'chosen_title_index': 0,
        },
        {
            'article_title': '苹果提醒用户更新iOS以免受网页攻击',
            'publish_date': '2026-04-15',
            'topic': '苹果iOS安全漏洞',
            'title_template': '警示式',
            'word_count': 980,
            'image_count': 3,
            'category': 'consumer_electronics',
            'tags': ['苹果', 'iOS', '安全'],
            'score_before_publish': 68,
        },
        {
            'article_title': '交管部门回应新能源车牌绿色变白色',
            'publish_date': '2026-04-14',
            'topic': '新能源车牌变色',
            'title_template': '冲突式',
            'word_count': 1105,
            'image_count': 4,
            'category': 'auto_tech',
            'tags': ['新能源车', '车牌', '交管'],
            'score_before_publish': 75,
        },
    ]
    
    print("\n[Step 1] 记录文章...")
    for art in test_articles:
        result = tracker.record_article(art)
        print(f"  {result['message']}")
    
    print("\n[Step 2] 模拟更新阅读数据...")
    
    # 模拟几天后的数据
    updates = [
        {'title_keyword': '姚安娜', 'read_count': 3580, 'like_count': 120, 'share_count': 45, 'comment_count': 28},
        {'title_keyword': '苹果', 'read_count': 2100, 'like_count': 65, 'share_count': 22, 'comment_count': 15},
        {'title_keyword': '车牌', 'read_count': 8920, 'like_count': 380, 'share_count': 156, 'comment_count': 92},
    ]
    
    for u in updates:
        result = tracker.update_performance(u['title_keyword'], u)
        print(f"  {result['message']}")
    
    print("\n[Step 3] 分析模式...")
    analysis = tracker.analyze_patterns()
    
    if analysis['status'] == 'ok':
        print(f"\n  总览:")
        print(f"  - 有数据文章: {analysis['summary']['total_articles_with_data']}篇")
        print(f"  - 平均阅读: {analysis['summary']['avg_reads']}")
        print(f"\n  Top文章:")
        for a in analysis.get('top_articles', []):
            print(f"  - {a['title'][:35]} | 阅读:{a['reads']} | {a['tier']}级")
        print(f"\n  建议:")
        for r in analysis.get('recommendations', []):
            print(f"  → {r}")
    
    print(f"\n  当前统计: {tracker.get_summary()}")
