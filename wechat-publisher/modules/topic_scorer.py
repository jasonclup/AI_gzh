# -*- coding: utf-8 -*-
"""
选题评分器 TopicScorer v1.0
对每个热点话题进行多维度打分，预测爆文潜力（0-100分）
维度：热度(25) + 争议性(20) + 时效性(15) + 赛道匹配(20) + 标题潜力(20)
"""

import re
import json
import random
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# 配置常量
# ============================================================

# 科技赛道高权重关键词（命中加分）
TECH_KEYWORDS_HIGH = {
    'AI': ['AI', 'GPT', 'ChatGPT', '大模型', '人工智能', 'DeepSeek', 'Kimi', 
           'Sora', 'Claude', 'Gemini', '通义', '文心', '混元', '智谱'],
    '芯片': ['芯片', '英伟达', 'NVIDIA', '台积电', '华为昇腾', 'EDA', '半导体',
             '摩尔定律', '2nm', '3nm', '7nm', '光刻机', '中芯'],
    '新能源车': ['新能源', '特斯拉', 'Tesla', '比亚迪', 'BYD', '蔚来', '小鹏',
                '理想', '问界', '小米汽车', 'FSD', '自动驾驶', '智驾',
                '固态电池', '换电', '充电桩', '绿牌'],
    '消费电子': ['iPhone', '苹果', 'Apple', '华为', '小米', 'OPPO', 'vivo',
               '三星', '折叠屏', 'Pura', 'Mate', 'MacBook', 'iPad',
               'Vision Pro', 'AirPods', 'Apple Watch'],
    '互联网平台': ['字节跳动', '抖音', 'TikTok', '腾讯', '微信', '阿里',
                 '拼多多', 'Temu', '小红书', '美团', '京东', '快手',
                 'B站', '哔哩', '知乎', '百度'],
    '智能硬件': ['无人机', 'DJI', '大疆', '机器人', 'VR', 'AR', 'MR',
               '智能家居', 'IoT', '穿戴设备', '耳机', '手表'],
}

# 所有高权重词的扁平列表
ALL_TECH_KEYWORDS = []
for kw_list in TECH_KEYWORDS_HIGH.values():
    ALL_TECH_KEYWORDS.extend(kw_list)

# 争议性/冲突关键词（命中说明有话题性）
CONTROVERSY_KEYWORDS = {
    # 高争议（+10~15分）
    'high': [
        '崩了', '翻车', '翻盘', '反转', '打脸', '造假', '骗局', '暴雷',
        '倒闭', '破产', '裁员', '封杀', '禁用', '下架', '召回',
        '起诉', '诉讼', '垄断', '罚款', '暴跌', '暴涨',
        '泄露', '隐私', '安全漏洞', '被黑', '数据泄露',
        '抄袭', '山寨', '侵权', '抄袭门',
        '翻车', '社死', '翻车现场', '翻车了',
    ],
    # 中等争议（+5~10分）
    'medium': [
        '争议', '质疑', '批评', '吐槽', '翻白眼', '不看好', '唱衰',
        '泡沫', '割韭菜', '智商税', '溢价', '不值', '劝退',
        '翻新', '二手', '降级', '缩水', '减配', '阉割',
        '翻新机', '水货', '假货', '山寨',
        '翻车', '翻新', '翻脸', '翻旧账',
    ],
    # 低争议但有关注度（+2~5分）
    'low': [
        '终于', '竟然', '居然', '没想到', '出乎意料', '意外',
        '曝光', '揭秘', '内幕', '真相', '实情', '背后',
        '对比', 'PK', '对决', '较量', '竞争', '挑战',
        '首发', '新品', '发布', '上市', '官宣', '确认',
    ],
}

# 时效性衰减规则（小时）
TIMELINESS_DECAY = {
    'hot': 6,      # 6小时内 = 满分
    'warm': 24,    # 24小时内 = 高分
    'normal': 48,  # 48小时内 = 中分
    'cold': 72,    # 72小时内 = 低分
    'stale': 168,  # 7天以上 = 极低
}

# 标题潜力关键词（能做出好标题的话题特征）
TITLE_POTENTIAL_SIGNALS = {
    # 数字信号（数字标题点击率高）
    'number': r'\d+[万亿百千万]|\d+亿|\d+%|\d+倍|\d+(?:万|千|百)?(?:元|块|人|次|台|辆|篇|条)',
    # 对比/反差信号
    'contrast': r'(?:比.*?好|不如|碾压|吊打|完胜|逆袭|反超|超过|落后|差距)',
    # 人物/品牌信号（有名有姓有点击欲）
    'brand': '|'.join(['英伟达', '华为', '苹果', '特斯拉', '小米', '字节', '腾讯',
                       '阿里', '比亚迪', '蔚来', '理想', '黄仁勋', '雷军',
                       '任正非', '马斯克', '库克', '李斌', '何小鹏', '李想']),
    # 情绪信号
    'emotion': r'(?:后悔|惊喜|震惊|愤怒|心疼|无语|哭笑不得|扎心|破防|真香|踩坑)',
}


# ============================================================
# 核心评分类
# ============================================================

class TopicScorer:
    """选题多维度评分器"""

    def __init__(self, config=None):
        self.config = config or {}
        # 权重配置（可自定义）
        self.weights = self.config.get('weights', {
            'heat': 25,         # 热度
            'controversy': 20,   # 争议性
            'timeliness': 15,    # 时效性
            'tech_match': 20,    # 赛道匹配度
            'title_potential': 20,  # 标题潜力
        })
        # 历史高分话题记录（用于去重和参考）
        self.history_path = Path(__file__).parent / "output" / "topic_scores_history.json"
        self._history = self._load_history()

    def _load_history(self):
        """加载历史评分记录"""
        try:
            if self.history_path.exists():
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_history(self):
        """保存历史评分记录（最近500条）"""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self._history[-500:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def score_topic(self, topic_data):
        """
        对单个热点话题进行全面评分
        
        Args:
            topic_data: dict, 包含以下字段：
                - title: str, 热点标题
                - summary: str, 热点摘要（可选）
                - source: str, 来源（可选）
                - hot_value: int/float, 热度值（可选）
                - publish_time: str, 发布时间（可选，ISO格式）
        
        Returns:
            dict: {
                'topic_title': str,
                'total_score': int (0-100),
                'grade': str (S/A/B/C/D),
                'dimensions': {各维度分数},
                'recommendation': str,
                'should_write': bool,
            }
        """
        title = topic_data.get('title', '')
        summary = topic_data.get('summary', '') or ''
        source = topic_data.get('source', '') or ''
        full_text = f"{title} {summary}"
        
        # 五个维度分别打分
        dim_heat = self._score_heat(topic_data, full_text)
        dim_controversy = self._score_controversy(full_text)
        dim_timeliness = self._score_timeliness(topic_data)
        dim_tech_match = self._score_tech_match(full_text)
        dim_title_potential = self._score_title_potential(title, full_text)
        
        # 加权总分
        total_score = (
            dim_heat * self.weights['heat'] +
            dim_controversy * self.weights['controversy'] +
            dim_timeliness * self.weights['timeliness'] +
            dim_tech_match * self.weights['tech_match'] +
            dim_title_potential * self.weights['title_potential']
        ) / 100  # 归一化到0-100
        
        total_score = min(100, max(0, round(total_score)))
        
        # 确定等级
        grade = self._get_grade(total_score)
        
        # 生成推荐建议
        recommendation = self._generate_recommendation(
            total_score, grade,
            dim_heat, dim_controversy, dim_timeliness,
            dim_tech_match, dim_title_potential,
            title
        )
        
        # 判断是否值得写（B级以上或总分>=60）
        should_write = total_score >= 60 or grade in ('S', 'A')
        
        result = {
            'topic_title': title[:80],
            'total_score': total_score,
            'grade': grade,
            'dimensions': {
                'heat': round(dim_heat, 1),
                'controversy': round(dim_controversy, 1),
                'timeliness': round(dim_timeliness, 1),
                'tech_match': round(dim_tech_match, 1),
                'title_potential': round(dim_title_potential, 1),
            },
            'recommendation': recommendation,
            'should_write': should_write,
            'scored_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # 记录历史
        self._history.append({
            'title': title[:80],
            'score': total_score,
            'grade': grade,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        })
        
        return result

    def score_topics_batch(self, topics_list):
        """
        批量评分并排序
        
        Returns:
            list[dict]: 已按总分降序排列的结果列表
        """
        results = [self.score_topic(t) for t in topics_list]
        results.sort(key=lambda x: x['total_score'], reverse=True)
        self._save_history()
        return results

    # ---- 各维度评分方法 ----

    def _score_heat(self, topic_data, full_text):
        """
        热度评分 (0-100)
        基于来源权重、热度值、搜索量关键词
        """
        score = 50  # 基础分
        
        source = (topic_data.get('source') or '').lower()
        hot_value = topic_data.get('hot_value')
        
        # 来源权重
        if '头条' in source or 'toutiao' in source:
            score += 15
        elif '微博' in source or 'weibo' in source:
            score += 12
        elif '知乎' in source or 'zhihu' in source:
            score += 10
        elif '百度' in source or 'baidu' in source:
            score += 8
        
        # 显式热度值
        if isinstance(hot_value, (int, float)):
            if hot_value >= 1000000:
                score += 30
            elif hot_value >= 500000:
                score += 25
            elif hot_value >= 100000:
                score += 18
            elif hot_value >= 50000:
                score += 12
            elif hot_value >= 10000:
                score += 6
            else:
                score += 3
        
        # 搜索热度信号词
        heat_signals = ['热搜', '热榜', '爆', '沸', '正在搜', '大家都在搜']
        for sig in heat_signals:
            if sig in full_text:
                score += 8
                break
        
        return min(100, max(0, score))

    def _score_controversy(self, text):
        """
        争议性评分 (0-100)
        基于冲突关键词、对立观点、情绪极化程度
        """
        score = 30  # 基础分（大部分科技话题都有一定讨论度）
        
        # 高争议词
        high_hits = sum(1 for kw in CONTROVERSY_KEYWORDS['high'] if kw in text)
        medium_hits = sum(1 for kw in CONTROVERSY_KEYWORDS['medium'] if kw in text)
        low_hits = sum(1 for kw in CONTROVERSY_KEYWORDS['low'] if kw in text)
        
        score += high_hits * 12 + medium_hits * 6 + low_hits * 3
        
        # 额外加分：同时出现"正面+负面"词汇（说明有分歧）
        positive_words = ['突破', '创新', '领先', '第一', '最强', '最好', '颠覆', '革命性']
        negative_words = ['问题', '风险', '缺陷', '不足', '失败', '落后', '下滑', '下跌']
        has_positive = any(w in text for w in positive_words)
        has_negative = any(w in text for w in negative_words)
        if has_positive and has_negative:
            score += 15  # 有分歧 = 有话题度
        
        return min(100, max(0, score))

    def _score_timeliness(self, topic_data):
        """
        时效性评分 (0-100)
        越新鲜越高分
        """
        score = 70  # 默认较高分（因为抓到的通常就是近期的）
        
        pub_time_str = topic_data.get('publish_time') or ''
        now = datetime.now()
        
        try:
            if pub_time_str:
                pub_time = datetime.fromisoformat(pub_time_str.replace('Z', '+00:00'))
                delta_hours = (now - pub_time).total_seconds() / 3600
                
                if delta_hours <= TIMELINESS_DECAY['hot']:
                    score = 95 + random.uniform(-5, 5)
                elif delta_hours <= TIMELINESS_DECAY['warm']:
                    score = 85 - (delta_hours - 6) * 1.2
                elif delta_hours <= TIMELINESS_DECAY['normal']:
                    score = 70 - (delta_hours - 24) * 0.8
                elif delta_hours <= TIMELINESS_DECAY['cold']:
                    score = 50 - (delta_hours - 48) * 0.5
                else:
                    score = 20
        except (ValueError, TypeError):
            pass  # 解析不了时间就用默认值
        
        return min(100, max(0, round(score)))

    def _score_tech_match(self, text):
        """
        赛道匹配度 (0-100)
        命中科技赛道关键词越多、越核心，分数越高
        """
        if not text.strip():
            return 0
        
        score = 40  # 大部分热点都跟科技沾点边
        
        hit_categories = set()
        hit_keywords = []
        
        for category, keywords in TECH_KEYWORDS_HIGH.items():
            for kw in keywords:
                if kw.lower() in text.lower():
                    hit_categories.add(category)
                    hit_keywords.append(kw)
                    break  # 每类只计一次
        
        # 分类命中数加权
        cat_count = len(hit_categories)
        if cat_count >= 4:
            score = 98
        elif cat_count >= 3:
            score = 90
        elif cat_count >= 2:
            score = 78
        elif cat_count >= 1:
            score = 65
        
        # 关键词密度加成
        keyword_density = len(hit_keywords) / max(len(text) / 10, 1)
        score += min(10, keyword_density * 20)
        
        return min(100, max(0, round(score)))

    def _score_title_potential(self, title, full_text):
        """
        标题潜力评分 (0-100)
        这个话题能不能做出吸引人点的标题？
        """
        if not title.strip():
            return 0
        
        score = 45  # 基础分
        
        # 数字信号
        if re.search(TITLE_POTENTIAL_SIGNALS['number'], title):
            score += 12
        
        # 对比/反差
        if re.search(TITLE_POTENTIAL_SIGNALS['contrast'], full_text):
            score += 14
        
        # 品牌/人物
        brand_hit = re.search(TITLE_POTENTIAL_SIGNALS['brand'], title)
        if brand_hit:
            score += 16
        elif re.search(TITLE_POTENTIAL_SIGNALS['brand'], full_text):
            score += 10
        
        # 情绪信号
        if re.search(TITLE_POTENTIAL_SIGNALS['emotion'], full_text):
            score += 13
        
        # 标题长度适中（太短没信息量，太长没人看）
        title_len = len(title)
        if 12 <= title_len <= 28:
            score += 8
        elif 8 <= title_len <= 35:
            score += 4
        
        # 问号/感叹号结尾（互动感强）
        if title.endswith(('？', '?', '！', '!')):
            score += 6
        
        return min(100, max(0, round(score)))

    # ---- 辅助方法 ----

    @staticmethod
    def _get_grade(score):
        """根据分数确定等级"""
        if score >= 85:
            return 'S'
        elif score >= 72:
            return 'A'
        elif score >= 58:
            return 'B'
        elif score >= 42:
            return 'C'
        else:
            return 'D'

    @staticmethod
    def _generate_recommendation(score, grade, heat, controversy,
                                  timeliness, tech_match, title_pot, title):
        """生成推荐语"""
        parts = []
        
        # 总评
        if grade == 'S':
            parts.append(f"[S级必写] 综合评分{score}，强烈推荐！")
        elif grade == 'A':
            parts.append(f"[A级推荐] 综合评分{score}，非常值得写")
        elif grade == 'B':
            parts.append(f"[B级可写] 综合评分{score}，可以写但非最优")
        elif grade == 'C':
            parts.append(f"[C级备选] 综合评分{score}，仅作备选或素材补充")
        else:
            parts.append(f"[D级跳过] 综合评分{score}，不建议写")
        
        # 维度亮点
        strengths = []
        if heat >= 75:
            strengths.append("热度极高")
        if controversy >= 70:
            strengths.append("争议性强（易引发讨论）")
        if timeliness >= 80:
            strengths.append("时效性好")
        if tech_match >= 80:
            strengths.append("完美匹配科技赛道")
        if title_pot >= 75:
            strengths.append("标题潜力大")
        
        if strengths:
            parts.append(f"亮点: {'+'.join(strengths)}")
        
        # 弱项提醒
        weaknesses = []
        if heat < 45:
            weaknesses.append("热度偏低")
        if controversy < 35:
            weaknesses.append("争议性弱（可能缺乏传播动力）")
        if tech_match < 50:
            weaknesses.append("与科技赛道关联度低")
        if title_pot < 40:
            weaknesses.append("标题不好做")
        
        if weaknesses and grade not in ('S', 'A'):
            parts.append(f"注意: {', '.join(weaknesses)}")
        
        return ' | '.join(parts)

    def get_top_n(self, topics_list, n=5, min_score=55):
        """获取Top N最佳选题"""
        scored = self.score_topics_batch(topics_list)
        top = [s for s in scored if s['total_score'] >= min_score][:n]
        return top


# ============================================================
# 便捷函数
# ============================================================

def quick_score(topics_list, top_n=5):
    """快速评分，返回Top N"""
    scorer = TopicScorer()
    return scorer.get_top_n(topics_list, n=top_n)


if __name__ == '__main__':
    # 测试
    test_topics = [
        {'title': '英伟达市值突破4万亿！黄仁勋这盘棋终于看懂了', 'source': '今日头条'},
        {'title': '苹果Vision Pro降价了，但我还是不推荐你买', 'summary': '苹果宣布Vision Pro降价2000元', 'source': '微博'},
        {'title': '某地天气转暖，市民纷纷出门踏青', 'source': '本地新闻', 'hot_value': 3000},
        {'title': 'DeepSeek炸场后，国内AI圈发生了什么没人告诉你', 'source': '今日头条', 'hot_value': 800000},
        {'title': '交管部门回应新能源车牌绿色变白色', 'source': '今日头条', 'hot_value': 500000},
        {'title': '某小区物业费调整通知', 'source': '社区公告'},
    ]
    
    scorer = TopicScorer()
    
    print("=" * 70)
    print("  选题评分测试")
    print("=" * 70)
    
    results = scorer.score_topics_batch(test_topics)
    
    print(f"\n{'排名':<4} {'标题':<38} {'总分':<6} {'等级':<4} {'是否推荐'}")
    print("-" * 75)
    
    for i, r in enumerate(results, 1):
        flag = "✅ 写!" if r['should_write'] else "⏭️ 跳过"
        print(f"{i:<4} {r['topic_title'][:36]:<38} {r['total_score']:<6} {r['grade']:<4} {flag}")
        dims = r['dimensions']
        print(f"     热度={dims['heat']} 争议={dims['controversy']} "
              f"时效={dims['timeliness']} 赛道={dims['tech_match']} 标题={dims['title_potential']}")
        print(f"     → {r['recommendation']}")
        print()
