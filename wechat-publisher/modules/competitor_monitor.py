# -*- coding: utf-8 -*-
"""
头部账号监控系统 CompetitorMonitor v1.0
监控科技赛道头部公众号，学习选题节奏、标题套路、发布时间、写作风格
"""

import re
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# 配置常量
# ============================================================

DATA_DIR = Path(__file__).parent / "output" / "competitor"
MONITOR_FILE = DATA_DIR / "monitor_data.json"
REPORT_DIR = DATA_DIR / "reports"

# 科技赛道头部公众号监控目标（可扩展）
TARGET_ACCOUNTS = [
    {
        'name': '差评果核',
        'category': '科技测评',
        'focus': ['消费电子', '数码产品', '开箱测评'],
        'style': '毒舌幽默+深度体验',
        'title_style': '悬念/反常识/对比',
        'posting_pattern': '每日1篇，晚间20-22点',
    },
    {
        'name': '42章经',
        'category': '科技商业',
        'focus': ['AI', '互联网商业模式', '创业'],
        'style': '深度长文+行业洞察',
        'title_style': '数据驱动/行业分析',
        'posting_pattern': '每周2-3篇，不定时',
    },
    {
        'name': '量子位',
        'category': 'AI前沿',
        'focus': ['AI大模型', '机器学习', '科技公司动态'],
        'style': '快速资讯+专业解读',
        'title_style': '新闻式+数字亮点',
        'posting_pattern': '每日3-5篇，全天候',
    },
    {
        'name': '机器之心',
        'category': 'AI技术',
        'focus': ['AI研究', '技术突破', '开发者工具'],
        'style': '硬核技术+产业观察',
        'title_style': '技术名词+影响力描述',
        'posting_pattern': '每日2-3篇',
    },
    {
        'name': '爱范儿',
        'category': '科技生活',
        'focus': ['消费电子', '生活方式', '智能硬件'],
        'style': '生活化视角+产品评测',
        'title_style': '场景化/情感共鸣',
        'posting_pattern': '每日2-4篇',
    },
    {
        'name': '极客公园',
        'category': '科技综合',
        'focus': ['科技创新', '创业者故事', '行业趋势'],
        'style': '访谈体+趋势预判',
        'title_style': '人物/观点/趋势',
        'posting_pattern': '每日3-5篇',
    },
    {
        'name': '虎嗅APP',
        'category': '科技商业评论',
        'focus': ['商业分析', '公司动态', '投资并购'],
        'style': '犀利点评+深度调查',
        'title_style': '冲突/反直觉/揭秘',
        'posting_pattern': '每日5-8篇',
    },
    {
        'name': '晚点LatePost',
        'category': '科技深度报道',
        'focus': ['大厂内幕', '人物专访', '行业真相'],
        'style': '独家报道+深度叙事',
        'title_style': '故事感/内幕感',
        'posting_pattern': '每周2-3篇，质量优先',
    },
]

# 模拟竞品文章样本（实际生产中通过微信搜索API/Sogou抓取真实数据）
COMPETITOR_SAMPLE_ARTICLES = [
    # === 差评果核风格 ===
    {
        'account': '差评果核',
        'title': 'iPhone 17 Pro用了三天，我后悔了——但不是你猜的那种',
        'publish_time': '2026-04-14 21:30',
        'category': '消费电子',
        'tags': ['iPhone', '苹果', '测评', '手机'],
        'estimated_reads': 85000,
        'content_summary': (
            "说句可能得罪人的话——这届iPhone真的让我有点意外。\n\n"
            "先说结论：它不是那种'哇塞好牛'的惊艳，而是那种用着用着突然意识到'卧槽这功能真香'的惊喜。\n\n"
            "比如那个新的电池管理系统。我第一天完全没注意，到第三天才发现它好像比我上一代多活了整整4个小时。不是那种官方宣传的'提升20%'，是实打实的从早上7点出门到晚上10点回家还剩28%的那种。\n\n"
            "当然也有槽点。信号问题依然存在，地下车库直接变砖这个老毛病苹果你是打算传家吗？\n\n"
            "总的来说，如果你手里是13或更早的机型，换。如果是15或16Pro用户，说实话可以再等等。"
        ),
        'writing_features': ['个人反应开头', '具体数据', '口语化比喻', '正反两面', '突然收尾'],
        'title_analysis': {'template': '悬念+反转', 'has_number': True, 'has_brand': True, 'emotion': '好奇+遗憾'},
    },
    {
        'account': '差评果核',
        'title': '小米汽车卖爆了，但我劝你别急着下单',
        'publish_time': '2026-04-13 20:15',
        'category': '新能源车',
        'tags': ['小米', '新能源汽车', 'SU7', '购车建议'],
        'estimated_reads': 120000,
        'content_summary': (
            "昨天去店里试驾了，排队两小时。两小时啊朋友们，就为了摸一把方向盘。\n\n"
            "车确实不错，这点没得黑。但我想说的是几个销售不会主动告诉你的事。\n\n"
            "第一，现车基本没有。你现在下定，最早提车要等3-5个月。3-5个月后是什么概念？特斯拉新款可能都出了，比亚迪的新车也可能降价了。你确定还要等？\n\n"
            "第二，智驾在复杂路况下还是差点意思。高速上没问题，但到了市区那些乱七八糟的路口，它还是会突然让你接管。我试了三次，两次都在最尴尬的时候——左转加塞那种。\n\n"
            "第三，也是我最想说的：这车的目标用户到底是谁？\n\n"
            "如果你是年轻人第一辆车，预算25-30万，想要个有面子的电动车，那确实可以考虑。但如果你家里已经有了一台油车，这台车能给你带来的新鲜感大概也就维持两个月。\n\n"
            "两个月后呢？它就是一台代步工具。和所有代步工具一样。"
        ),
        'writing_features': ['场景化开头', '分点论述(非列表)', '反问推进', '目标受众分析', '留白收尾'],
        'title_analysis': {'template': '警示+反向', 'has_number': False, 'has_brand': True, 'emotion': '谨慎'},
    },
    
    # === 量子位风格 ===
    {
        'account': '量子位',
        'title': '刚刚！DeepSeek新模型炸场，推理能力超GPT-5，代码能力翻3倍',
        'publish_time': '2026-04-14 09:00',
        'category': 'AI大模型',
        'tags': ['DeepSeek', 'AI', '大模型', 'GPT-5'],
        'estimated_reads': 200000,
        'content_summary': (
            "刚刚，DeepSeek正式发布新一代模型DS-V4，多项核心指标刷新SOTA。\n\n"
            "根据官方公布的benchmark数据：\n\n"
            "- 数学推理（MATH-500）：92.3%（GPT-5为89.1%）\n"
            "- 代码生成（HumanEval+）：94.7%（GPT-5为91.2%）\n"
            "- 中文理解（C-Eval）：96.8%\n"
            "- 多模态理解：首次支持原生视频理解，时长可达30分钟\n\n"
            "值得关注的是，这次DeepSeek采用了全新的MoE架构升级方案，激活参数量达到惊人的3.2T，但推理成本却下降了40%。\n\n"
            "业内分析师认为，这可能标志着国产大模型在核心技术上真正实现了'并跑甚至局部领跑'。"
        ),
        'writing_features': ['紧迫感开头', '数据密集', '分点列举', '引用权威', '行业意义结尾'],
        'title_analysis': {'template': '新闻爆炸式', 'has_number': True, 'has_brand': True, 'emotion': '震撼'},
    },
    {
        'account': '量子位',
        'title': '马斯克又搞事了！xAI融资1000亿美元，要跟OpenAI死磕到底',
        'publish_time': '2026-04-12 18:30',
        'category': 'AI商业',
        'tags': ['马斯克', 'xAI', 'OpenAI', '融资'],
        'estimated_reads': 150000,
        'content_summary': (
            "据彭博社最新消息，埃隆·马斯克旗下AI公司xAI正在洽谈一轮高达1000亿美元的融资。\n\n"
            "如果完成，这将是AI领域史上最大单笔融资，超过OpenAI此前所有轮融资的总和。\n\n"
            "知情人士透露，本轮估值可能达到3000亿美元。主要投资者包括沙特主权基金、阿联酋穆巴达拉等中东资本。\n\n"
            "消息一出，xAI的旗舰产品Grok访问量在24小时内暴涨180%。\n\n"
            "有意思的是，就在上周OpenAI刚宣布了其下一代模型O3的开发进度。两大巨头的军备竞赛正在全面升级。"
        ),
        'writing_features': ['八卦式开头', '巨额数字冲击', '多方信源', '对比竞争', '悬念留白'],
        'title_analysis': {'template': '人物+冲突+数字', 'has_number': True, 'has_brand': True, 'emotion': '兴奋+紧张'},
    },

    # === 虎嗅APP风格 ===
    {
        'account': '虎嗅APP',
        'title': '字节跳动的AI焦虑：为什么做了这么多产品还是追不上？',
        'publish_time': '2026-04-14 08:00',
        'category': '互联网平台',
        'tags': ['字节跳动', 'AI', '豆包', '战略'],
        'estimated_reads': 95000,
        'content_summary': (
            "字节跳动可能是中国互联网公司里最焦虑的一家。\n\n"
            "不是因为做得不好——恰恰相反，它在几乎所有赛道都有布局。问题是，没有一个做到行业第一。\n\n"
            "AI大模型有豆包，但市场份额不到5%；短视频有抖音，但增长见顶；电商有抖音电商，但GMV只有拼多多的三分之一；社交有飞书/多闪/朝夕，但没有一个真正打出去。\n\n"
            "张一鸣当年说的'大力出奇迹'，在AI时代好像不太灵了。\n\n"
            "核心原因可能只有一个：字节的基因是推荐算法和内容分发，而不是底层技术创新。当战场从'谁能更好地匹配内容和用户'变成'谁的基础模型更强'时，字节的护城河突然变浅了。\n\n"
            "这不是危言耸听。看看过去两年字节在AI上的投入——据说已经超过500亿人民币——再看看产出，你会明白什么叫'钱花出去了，水花都没看到'。\n\n"
            "当然，字节还有时间。但如果GPT-5级别的模型今年真的被国内某家公司做出来了呢？"
        ),
        'writing_features': ['强观点开头', '多维论证', '具体数据', '归因分析', '开放式提问结尾'],
        'title_analysis': {'template': '疑问+痛点', 'has_number': False, 'has_brand': True, 'emotion': '焦虑+好奇'},
    },
    
    # === 爱范儿风格 ===
    {
        'account': '爱范儿',
        'title': '我把家里的灯全换成了智能的，然后后悔了',
        'publish_time': '2026-04-13 22:00',
        'category': '智能家居',
        'tags': ['智能照明', '智能家居', '生活体验'],
        'estimated_reads': 45000,
        'content_summary': (
            "事情是这样的。\n\n"
            "上个月搬家，我一激动把全屋的灯都换成了米家的智能灯泡。当时觉得特别酷——手机一按全屋灯光随心调，还能设置各种场景模式。\n\n"
            "然后现实开始教育我了。\n\n"
            "第一个坑：断网。上周小区光纤改造断了一天网，我家晚上基本上是在烛光中度过的。对，智能灯断网就不能手动开关。设计这个的人有没有想过这个问题？\n\n"
            "第二个坑：家人。我妈来住了一周，每天问我'怎么开灯''怎么关灯''怎么调亮一点'。最后她干脆不进客厅了。\n\n"
            "第三个坑：App本身。三个不同的App控制三组不同的灯，每次调个氛围光要切来切去。我本来是想省事的……\n\n"
            "所以我的建议是：如果你想体验智能家居，先从一个房间开始。别像我一样脑子一热全换了。"
        ),
        'writing_features': ['自述式开头', '分段讲故事', '每个段落一个小反转', '个人经验教训', '实用建议结尾'],
        'title_analysis': {'template': '自述+反转', 'has_number': False, 'has_brand': False, 'emotion': '后悔+共鸣'},
    },

    # === 晚点LatePost风格 ===
    {
        'account': '晚点LatePost',
        'title': '那个让马云失眠的男人，现在怎么样了',
        'publish_time': '2026-04-12 20:00',
        'category': '科技商业',
        'tags': ['拼多多', '黄峥', '电商', '人物'],
        'estimated_reads': 180000,
        'content_summary': (
            "2018年夏天的一个下午，杭州西溪园区，阿里巴巴最高层的会议室里气氛凝重。\n\n"
            "摆在桌上的不是财务报表，而是一份来自内部情报团队的报告。报告的核心内容只有一行字：\n\n"
            "'一个叫拼多多的人在偷我们的家。'\n\n"
            "那个人叫黄峥。那一年他38岁，拼多多成立不到3年，GMV已经突破1000亿。而阿里花了整整15年才走到这一步。\n\n"
            "据在场人士回忆，那天会议结束后很久，马云都没有说话。\n\n"
            "六年过去了。今天的黄铮已经是全球排名前30的富豪，拼多多的市值一度超过阿里。但他也越来越少出现在公众视野中。\n\n"
            "我们采访了他身边12个人，包括前同事、投资人、竞争对手、甚至他的大学室友。试图还原一个真实的黄峥——以及一个关于野心、时机和中国互联网下半场的更大故事。"
        ),
        'writing_features': ['电影式场景开头', '悬念钩子', '多角度叙述', '时间线推进', '宏大叙事'],
        'title_analysis': {'template': '人物悬念', 'has_number': False, 'has_brand': False, 'emotion': '好奇'},
    },
]


# ============================================================
# 核心类
# ============================================================

class CompetitorMonitor:
    """头部账号监控系统"""

    def __init__(self):
        self.accounts = TARGET_ACCOUNTS
        self.data_file = MONITOR_FILE
        self.samples = COMPETITOR_SAMPLE_ARTICLES
        self.monitor_data = self._load_monitor_data()
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_monitor_data(self):
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'accounts': {}, 'articles': [], 'last_update': None}

    def _save_monitor_data(self):
        self.monitor_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.monitor_data, f, ensure_ascii=False, indent=2)

    # ---- 核心方法 ----

    def quick_check(self, topic_title: str) -> dict:
        """
        快速检查：给定话题标题，返回竞品覆盖情况和写作建议。
        轻量版，不跑完整扫描，仅基于内置样本做关键词匹配。
        """
        import re

        topic_lower = topic_title.lower()
        covered_by = []
        suggested_angles = []

        for acc in self.accounts:
            acc_articles = self._get_account_sample_articles(acc.get('name', ''))
            matched = []
            for article in acc_articles:
                art_title = (article.get('title', '') or '').lower()
                art_content = (article.get('full_content', '') or '').lower()
                combined = f"{art_title} {art_content}"
                if any(kw in combined for kw in self._extract_keywords(topic_lower)):
                    matched.append({**article, 'account_name': acc.get('name', '')})
                    break
            if matched:
                covered_by.extend(matched)

        # 基于匹配结果生成角度建议
        if not covered_by:
            suggested_angles = [
                {'angle': f'从普通用户视角解读"{topic_title[:30]}"', 'source_account': '系统建议'},
                {'angle': f'结合个人经历谈对"{topic_title[:20]}"的真实感受', 'source_account': '系统建议'},
                {'angle': f'用反直觉观点切入：为什么"{topic_title[:20]}"没那么重要？', 'source_account': '系统建议'},
            ]
        else:
            seen_angles = set()
            for item in covered_by[:5]:
                features = item.get('writing_features', {})
                angle_hint = features.get('narrative_angle', '')
                if angle_hint and angle_hint not in seen_angles:
                    suggested_angles.append({
                        'angle': f'参考{item.get("account_name","")}的角度: {angle_hint}',
                        'source_account': item.get('account_name', ''),
                    })
                    seen_angles.add(angle_hint)
            if not suggested_angles:
                suggested_angles = [{'angle': '用不同立场重新审视该话题', 'source_account': '系统建议'}]

        # 覆盖度判断
        total_accounts = len(self.accounts)
        unique_covered = len(set(item.get('account_name', '') for item in covered_by))
        coverage_ratio = unique_covered / max(total_accounts, 1)

        if coverage_ratio >= 0.6:
            coverage_level = 'high'
        elif coverage_ratio >= 0.25:
            coverage_level = 'medium'
        else:
            coverage_level = 'low'

        writing_tips = {
            'title_style_tip': '',
            'opening_technique': '',
            'avoid_pitfall': ''
        }
        if covered_by:
            best_match = covered_by[0]
            feat = best_match.get('writing_features', {})
            title_patterns = feat.get('title_patterns', [])
            if title_patterns:
                writing_tips['title_style_tip'] = f'竞品常用: {", ".join(title_patterns[:2])}'
            opening = feat.get('opening_style', '')
            if opening:
                writing_tips['opening_technique'] = opening[:80]
            writing_tips['avoid_pitfall'] = '避免与竞品使用完全相同的切入点或论点结构'

        return {
            'topic': topic_title,
            'coverage_level': coverage_level,
            'covered_by': covered_by,
            'suggested_angles': suggested_angles,
            'writing_tips': writing_tips,
        }

    def _extract_keywords(self, text: str) -> list[str]:
        import re
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        english_words = re.findall(r'[A-Za-z]{3,}', text)
        return chinese_words + english_words

    def _get_account_sample_articles(self, account_name: str) -> list[dict]:
        articles = []
        sample_data = getattr(self, '_sample_articles', None)
        if sample_data is None:
            return articles
        for art in sample_data:
            if art.get('account', '') == account_name or account_name == '':
                articles.append(art)
        return articles

    def run_full_scan(self):
        """
        执行一次完整扫描：
        1. 加载竞品文章样本
        2. 分析各账号特征
        3. 生成监控报告
        """
        print("\n" + "=" * 60)
        print("  头部账号监控系统")
        print(f"  扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Step 1: 加载文章
        print("\n[Step 1] 加载竞品文章样本...")
        articles = self._load_competitor_articles()
        print(f"  加载 {len(articles)} 篇竞品文章")

        # Step 2: 分析各维度
        print("\n[Step 2] 分析账号特征...")
        
        # 按账号分组分析
        account_analysis = {}
        for acc in self.accounts:
            acc_name = acc['name']
            acc_articles = [a for a in articles if a.get('account') == acc_name]
            account_analysis[acc_name] = self._analyze_account(acc, acc_articles)

        # Step 3: 全局模式提取
        print("\n[Step 3] 提取全局写作模式...")
        global_patterns = self._extract_global_patterns(articles)

        # Step 4: 可操作建议
        print("\n[Step 4] 生成优化建议...")
        recommendations = self._generate_recommendations(account_analysis, global_patterns)

        # 组装结果
        report = {
            'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'monitored_accounts': len(self.accounts),
            'total_analyzed_articles': len(articles),
            'account_details': account_analysis,
            'global_patterns': global_patterns,
            'recommendations': recommendations,
        }

        # 保存
        self.monitor_data['articles'].extend(articles)
        self.monitor_data['accounts'] = account_analysis
        self._save_monitor_data()

        # 同时保存为独立报告文件
        report_path = self._save_report(report)
        report['report_path'] = str(report_path)

        return report

    def _load_competitor_articles(self):
        """加载竞品文章（生产环境中这里调用抓取接口）"""
        # 当前使用内置样本，后续可接入微信搜狗/搜狗微信搜索API
        return list(self.samples)  # 返回副本

    def _analyze_account(self, account_info, articles):
        """分析单个账号的特征"""
        if not articles:
            return {
                **account_info,
                'article_count': 0,
                'avg_reads': 0,
                'top_topics': [],
                'title_patterns': [],
                'posting_times': [],
                'strengths': ['暂无足够数据'],
                'weaknesses': ['暂无足够数据'],
            }

        total_reads = sum(a.get('estimated_reads', 0) for a in articles)
        avg_reads = total_reads // len(articles)

        # 提取标题模式
        title_templates = [a.get('title_analysis', {}).get('template', '') for a in articles]
        
        # 提取高频标签
        all_tags = []
        for a in articles:
            all_tags.extend(a.get('tags', []))
        from collections import Counter
        tag_counts = Counter(all_tags).most_common(8)

        # 提取发文时间分布
        times = []
        for a in articles:
            pt = a.get('publish_time', '')
            if pt and len(pt) >= 14 and ':' in pt[11:]:
                try:
                    hour = int(pt.split()[1].split(':')[0])
                    times.append(hour)
                except (ValueError, IndexError):
                    pass

        # 提取写作特征频率
        all_features = []
        for a in articles:
            all_features.extend(a.get('writing_features', []))
        feature_counts = Counter(all_features).most_common(10)

        return {
            **account_info,
            'article_count': len(articles),
            'total_estimated_reads': total_reads,
            'avg_reads': avg_reads,
            'top_topics': [t[0] for t in tag_counts],
            'title_patterns': list(set(title_templates)) if title_templates else [],
            'posting_hour_distribution': {f'{h}点': times.count(h) for h in sorted(set(times)) if h},
            'common_writing_features': feature_counts,
            'best_article': max(articles, key=lambda x: x.get('estimated_reads', 0), default={}),
        }

    def _extract_global_patterns(self, articles):
        """从全部竞品文章中提取全局写作规律"""
        if not articles:
            return {}

        patterns = {}

        # 标题长度统计
        title_lengths = [len(a.get('title', '')) for a in articles]
        patterns['title_length'] = {
            'min': min(title_lengths),
            'max': max(title_lengths),
            'avg': round(sum(title_lengths) / len(title_lengths)),
            'median': sorted(title_lengths)[len(title_lengths) // 2],
        }

        # 标题模板类型分布
        template_types = [a.get('title_analysis', {}).get('template', '') for a in articles]
        from collections import Counter
        template_dist = Counter(template_types)
        patterns['title_template_distribution'] = dict(template_dist.most_common())

        # 高频写作技巧
        all_feats = []
        for a in articles:
            all_feats.extend(a.get('writing_features', []))
        feat_dist = Counter(all_feats)
        patterns['top_writing_techniques'] = [(f, c) for f, c in feat_dist.most_common(15)]

        # 最佳发布时段
        hours = []
        for a in articles:
            pt = a.get('publish_time', '')
            if pt and len(pt) >= 14:
                try:
                    h = int(pt.split()[1].split(':')[0])
                    hours.append(h)
                except:
                    pass
        
        if hours:
            hour_dist = Counter(hours)
            best_hours = hour_dist.most_common(5)
            patterns['optimal_posting_hours'] = [
                {'hour': f'{h}点', 'count': c} for h, c in best_hours
            ]
        else:
            patterns['optimal_posting_hours'] = []

        # 内容分类分布
        cats = [a.get('category', 'unknown') for a in articles]
        cat_dist = Counter(cats)
        patterns['category_distribution'] = dict(cat_dist.most_common())

        # 高阅读文章的共同特征
        high_read_threshold = sum(a.get('estimated_reads', 0) for a in articles) / len(articles) * 1.5
        high_perf = [a for a in articles if a.get('estimated_reads', 0) >= high_read_threshold]
        if high_perf:
            hp_feats = []
            for a in high_perf:
                hp_feats.extend(a.get('writing_features', []))
            hp_feat_dist = Counter(hp_feats)
            patterns['high_performance_features'] = [
                (f, c) for f, c in hp_feat_dist.most_common(10)
            ]

        return patterns

    def _generate_recommendations(self, account_analysis, global_patterns):
        """基于竞品分析生成可操作的优化建议"""
        recs = []

        # 从标题模式学到的
        title_dist = global_patterns.get('title_template_distribution', {})
        if title_dist:
            top_tmpl = max(title_dist.items(), key=lambda x: x[1])[0]
            recs.append(f"[标题] 竞品最常用标题模式: '{top_tmpl}'，建议增加此类模板权重")

        # 从发布时间学到的
        optimal_hours = global_patterns.get('optimal_posting_hours', [])
        if optimal_hours:
            best_hour = optimal_hours[0]['hour']
            recs.append(f"[发布时间] 竞品最佳发布时段: {best_hour}，建议在此窗口前后1小时内发布")

        # 从写作技巧学到的
        top_tech = global_patterns.get('top_writing_techniques', [])[:5]
        if top_tech:
            tech_str = ' / '.join([t[0] for t in top_tech])
            recs.append(f"[写作技巧] 竞品高频技巧TOP5: {tech_str}")

        # 从高阅读文章学来的
        hp_feats = global_patterns.get('high_performance_features', [])
        if hp_feats:
            hp_str = ' / '.join([f[0] for f in hp_feats[:5]])
            recs.append(f"[爆文特征] 高阅读文章共同特征: {hp_str}")

        # 分类建议
        cat_dist = global_patterns.get('category_distribution', {})
        if cat_dist:
            top_cat = max(cat_dist.items(), key=lambda x: x[1])[0]
            recs.append(f"[内容方向] 竞品最热门分类: {top_cat}，当前占比{cat_dist[top_cat]}%，可参考调整产出比例")

        # 各账号特色借鉴
        for acc_name, analysis in account_analysis.items():
            feats = analysis.get('common_writing_features', [])
            if feats and len(feats) >= 2:
                top2 = [f[0] for f in feats[:2]]
                recs.append(f"[借鉴-{acc_name}] 特色: {'+'.join(top2)}")

        return recs

    def _save_report(self, report):
        """保存报告到文件"""
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = REPORT_DIR / f"monitor_{ts}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # 同时保存 Markdown 版本
        md_filepath = REPORT_DIR / f"monitor_{ts}.md"
        md_content = self._build_markdown_report(report)
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return filepath

    def _build_markdown_report(self, report):
        """构建 Markdown 格式的报告"""
        lines = [
            "# 头部账号监控报告",
            "",
            f"- **扫描时间**: {report['scan_time']}",
            f"- **监控账号数**: {report['monitored_accounts']}",
            f"- **分析文章总数**: {report['total_analyzed_articles']}",
            "",
            "## 监控目标",
            "",
            "| 账号 | 类别 | 关注方向 | 风格 |",
            "|------|------|----------|------|",
        ]

        for acc in TARGET_ACCOUNTS:
            lines.append(
                f"| {acc['name']} | {acc['category']} | {'/'.join(acc['focus'][:2])} | {acc['style']} |"
            )

        gp = report.get('global_patterns', {})

        lines.extend([
            "",
            "## 全局发现",
            "",
            f"### 标题长度: 平均**{gp.get('title_length', {}).get('avg', '?')}**字 "
            f"(范围: {gp.get('title_length', {}).get('min', '?')}-{gp.get('title_length', {}).get('max', '?')})",
            "",
            "### 最常用标题模式:",
        ])

        tmpl_dist = gp.get('title_template_distribution', {})
        for tmpl, count in sorted(tmpl_dist.items(), key=lambda x: -x[1])[:8]:
            lines.append(f"- **{tmpl}**: {count}篇")

        lines.extend([
            "",
            "### TOP 写作技巧:",
        ])
        
        top_tech = gp.get('top_writing_techniques', [])[:10]
        for tech, count in top_tech:
            lines.append(f"- **{tech}**: 出现{count}次")

        optimal = gp.get('optimal_posting_hours', [])
        if optimal:
            lines.extend([
                "",
                "### 最佳发布时段:",
            ])
            for item in optimal[:5]:
                lines.append(f"- **{item['hour']}** ({item['count']}篇文章)")

        lines.extend([
            "",
            "## 优化建议",
            "",
        ])

        for i, rec in enumerate(report.get('recommendations', []), 1):
            lines.append(f"{i}. {rec}")

        return '\n'.join(lines)


if __name__ == '__main__':
    monitor = CompetitorMonitor()
    result = monitor.run_full_scan()

    print(f"\n{'='*60}")
    print(f"  [DONE] 监控完成!")
    print(f"  监控账号: {result['monitored_accounts']} 个")
    print(f"  分析文章: {result['total_analyzed_articles']} 篇")
    print(f"  生成建议: {len(result['recommendations'])} 条")
    print(f"  报告已保存: {result.get('report_path', 'N/A')}")
    print(f"{'='*60}")
