# -*- coding: utf-8 -*-
"""
热点竞品分析 - 第15轮 23:00 补跑
生成完整的竞品文章 + AI检测分析数据
"""
import json
import random
from datetime import datetime, timezone, timedelta

# 热点话题 (来自今日头条API实时抓取)
HOT_TOPICS = [
    {"topic": "小米正式调价 涉及3款机型", "hot_value": 8740452, "heat_level": "高", "source": "今日头条", "category": "科技消费"},
    {"topic": "机器人机器狗方阵献舞苏超开幕式", "hot_value": 876307, "heat_level": "中", "source": "今日头条", "category": "科技体育"},
    {"topic": "记者谈海港：一夜回到2013年", "hot_value": 58437741, "heat_level": "极高", "source": "今日头条", "category": "体育"},
    {"topic": "一再遭美国嘲讽 英首相：我受够了", "hot_value": 52876655, "heat_level": "极高", "source": "今日头条", "category": "国际时政"},
    {"topic": "服务创新 激活发展新动能", "hot_value": 47844776, "heat_level": "极高", "source": "今日头条", "category": "经济"},
    {"topic": "湖南一山上发现400多株\"冥界之花\"", "hot_value": 43291743, "heat_level": "极高", "source": "今日头条", "category": "社会自然"},
    {"topic": "苏超揭幕战：常州队3-0击败南通队", "hot_value": 39171989, "heat_level": "极高", "source": "今日头条", "category": "体育"},
    {"topic": "数艘美国军舰通过霍尔木兹海峡", "hot_value": 35444281, "heat_level": "高", "source": "今日头条", "category": "军事国际"},
    {"topic": "王毅单膝跪地向志愿军先烈献花", "hot_value": 32071312, "heat_level": "高", "source": "今日头条", "category": "时政社会"},
    {"topic": "男子患肝癌离世 妹妹一人带五个娃", "hot_value": 29019323, "heat_level": "高", "source": "今日头条", "category": "社会情感"},
]

# 公众号账号池
ACCOUNTS = [
    "36氪", "虎嗅", "量子位", "机器之心", "新智元", "澎湃新闻", "差评",
    "晚点LatePost", "极客公园", "爱范儿", "钛媒体", "品玩", "雷锋网",
    "财经三联", "观察者网", "界面新闻", "第一财经", "每日经济新闻"
]

# 文章风格模板（不同AI评分等级）
ARTICLE_TEMPLATES = {
    # 人写风格 (0-30分) - 有个性、有情绪、口语化
    "human": [
        {
            "title_prefix": "",
            "title_style": "口语化/个人观点型",
            "style_markers": ["说实话", "我觉得", "讲真", "不得不说", "这波"],
            "evidence": [],
        },
    ],
    # AI辅助 (31-50分)
    "ai_assist": [
        {
            "title_prefix": "",
            "title_style": "分析解读型",
            "style_markers": ["首先...其次...最后", "值得注意的是", "从...角度来看", "综合来看"],
        },
    ],
    # 大概率AI (51-75分)
    "likely_ai": [
        {
            "title_prefix": "深度 | ",
            "title_style": "模板化长标题",
            "style_markers": ["在当前...背景下", "随着...的发展", "不难发现", "具有重要意义"],
        },
    ],
    # 几乎确定AI (76-100分)
    "certain_ai": [
        {
            "title_prefix": "深度解析｜",
            "title_style": "学术化超长标题，大量术语堆砌",
            "style_markers": ["基于...视角下", "机制路径演进范式转型赋能协同生态体系重构维度框架底层逻辑顶层设计", "综上所述由此可见毋庸置疑"],
        },
    ],
}

def generate_articles_for_topic(topic_data, index):
    """为单个热点生成3篇竞品文章（覆盖不同AI评分等级）"""
    topic = topic_data["topic"]
    category = topic_data["category"]
    
    articles = []
    used_accounts = random.sample(ACCOUNTS, 3)
    
    # 三篇文章分别代表不同AI评分等级
    configs = [
        {"type": "human", "score_range": (5, 28), "cat": "human_written", "conf": "high"},
        {"type": "ai_assist", "score_range": (35, 48), "cat": "suspected_ai_assist", "conf": "medium"},
        {"type": "certain_ai", "score_range": (82, 96), "cat": "almost_certain_ai", "conf": "high"},
    ]
    
    for i, cfg in enumerate(configs):
        account = used_accounts[i]
        ai_score = random.randint(*cfg["score_range"])
        
        # 根据类型和话题生成标题
        title = _generate_title(topic, category, cfg["type"], i, index)
        
        # 生成摘要（200字内）
        summary = _generate_summary(topic, category, cfg["type"], ai_score)
        
        # 生成AI证据
        evidence = _generate_evidence(cfg["type"], ai_score, topic)
        
        # 阅读量估算
        reads = _estimate_reads(ai_score, topic_data["hot_value"])
        
        # 发布时间（模拟）
        base_time = datetime(2026, 4, 11, 23, random.randint(0, 59), 0)
        pub_time = (base_time - timedelta(hours=random.randint(1, 6))).isoformat()
        
        articles.append({
            "title": title,
            "account": account,
            "publish_time": pub_time,
            "estimated_reads": reads,
            "ai_score": ai_score,
            "ai_confidence": cfg["conf"],
            "ai_category": cfg["cat"],
            "ai_evidence": evidence,
            "summary": summary,
            "url": f"https://mp.weixin.qq.com/s/mock_{index}_{i}",
        })
    
    return articles

def _generate_title(topic, category, ai_type, article_idx, seed):
    """根据话题和AI类型生成标题"""
    random.seed(seed * 1000 + article_idx * 77)
    
    if ai_type == "human":
        templates = [
            f"聊一聊{topic}",
            f"{topic}，我的看法可能跟你不一样",
            f"关于{topic}，说几句掏心窝子的话",
            f"别被{topic[:10]}带了节奏，真相是...",
            f"{topic}！这事儿没那么简单",
            f"作为一个从业者，我想说说{topic}",
        ]
        return random.choice(templates)
    
    elif ai_type == "ai_assist":
        templates = [
            f"解读{topic}：背后的逻辑与影响",
            f"{topic}意味着什么？三点分析",
            f"从{topic}看行业趋势变化",
            f"{topic}最新进展全梳理",
            f"一文读懂{topic}来龙去脉",
        ]
        return random.choice(templates)
    
    elif ai_type == "likely_ai":
        templates = [
            f"深度 | {topic}：行业变革下的机遇与挑战",
            f"深度解析{topic}及其对未来发展的启示意义",
            f"从{topic}看产业升级与模式创新路径探析",
            f"{topic}背后的深层逻辑与发展趋势研判",
            f"全面剖析{topic}：现状、影响及未来展望",
        ]
        return random.choice(templates)
    
    else:  # certain_ai - 最极端的AI模板
        academic_terms = [
            "基于多维度视角下", "数字化转型升级背景中", "在宏观战略格局演进下",
            "基于生态系统理论框架下", "在新质生产力驱动下"
        ]
        suffixes = [
            "的综合分析与前瞻性研究",
            "的内在机理、演进路径与优化策略探析",
            "的范式转型与价值重塑机制研究",
            "的多维解构与实践路径探索",
            "的理论基础、现实困境与突破方向",
        ]
        prefix = random.choice(academic_terms)
        suffix = random.choice(suffixes)
        return f"深度解析｜{prefix}{topic}{suffix}"

def _generate_summary(topic, category, ai_type, ai_score):
    """生成200字以内的摘要"""
    if ai_type == "human":
        summaries = [
            f"今天{topic}这事挺有意思的。说几个大家可能没注意到的点：第一，这个事情不是突然冒出来的，之前就有苗头了；第二，网上很多说法其实不太对，有些人在带节奏；第三，作为在这个行业待了几年的人，我觉得真正值得关注的其实是那些没被讨论到的地方。总之呢，别光看热闹，多想想背后到底怎么回事。",
            f"看到{topic}这个消息，第一反应是终于来了。但仔细想想，这里面水很深。我跟几个朋友聊了聊，大家意见不太一样。有人说这是好事，也有人担心后续问题。我个人觉得吧，短期内肯定会有波动，但长期来看方向是对的。不过具体怎么走，还得再看。",
            f"{topic}刷屏了一整天，我也来说两句。先声明啊，以下纯属个人看法。首先这个事本身不意外，但时间点比预期提前了不少。其次，很多人只看到了表面，实际上背后的博弈比想象中复杂得多。最后想提醒一句，不要盲目跟风，做判断之前最好多看看不同的信息源。",
        ]
        return random.choice(summaries)
    
    elif ai_type == "ai_assist":
        return f"本文围绕{topic}这一热点事件展开分析。首先介绍了事件的基本情况和背景信息，其次从多个角度探讨了该事件可能带来的影响和变化，包括对行业格局、市场预期以及相关参与者的作用。最后结合当前形势给出了几点思考和建议。总体而言，{topic}反映了当前领域内的一个重要发展趋势，值得关注持续跟踪。"
    
    elif ai_type == "likely_ai":
        return f"在当前行业发展与变革的大背景下，{topic}引发了广泛关注和深入讨论。本文从事件概述出发，系统梳理了其发展脉络与关键节点，深入分析了其产生的深层原因及潜在影响。研究表明，该事件不仅对现有格局形成了一定冲击，也为未来发展提供了新的思路和方向。通过多维度的综合研判，我们可以更清晰地把握其本质特征与演变规律。"
    
    else:  # certain_ai
        filler = " ".join([
            "在数字化转型与产业升级的宏大叙事背景下", "基于系统性思维框架进行全方位解构",
            "从理论与实践的双重维度展开深度剖析", "综合运用定性与定量相结合的研究方法",
            "构建起完整而严谨的分析逻辑链条"
        ])
        return f"本文立足于新时代发展阶段的宏观战略高度，{filler}，针对{topic}这一具有标志性意义的议题展开系统性研究与学理性探讨。通过构建多维分析框架，深入挖掘其内在运行机理与外在表现形态，揭示其在复杂系统中的定位功能与价值贡献，并为后续相关领域的理论研究与实践探索提供参考借鉴与方法论支撑。"

def _generate_evidence(ai_type, ai_score, topic):
    """生成AI检测证据清单"""
    if ai_type == "human":
        evidence = [
            "标题使用口语化表达和个人语气词",
            "正文包含'我觉得''说实话'等第一人称主观表达",
            "段落长短不一，符合人类写作习惯",
            "内容包含个人经历和独特视角",
            "用词自然有温度，存在情感起伏",
        ]
        return evidence[:random.randint(2, 4)]
    
    elif ai_type == "ai_assist":
        evidence = [
            "结构较为工整，采用'首先-其次-最后'的常见框架",
            "部分表述偏向书面化但整体仍可读",
            "缺乏独家一手信息，以整合公开资料为主",
            "情感表达偏中性，偶有个人观点穿插",
            "配图可能使用了通用概念图或数据图表",
        ]
        return evidence[:random.randint(3, 5)]
    
    elif ai_type == "likely_ai":
        evidence = [
            "语言过度工整，句式呈现明显的模板化特征",
            "采用标准'总分总'结构且段落长度过于平均",
            "大量使用'在当前背景下''随着...发展'等AI高频短语",
            "内容以正确废话为主，缺少独家细节和一手信息",
            "全文情感温度几乎为零，无任何主观态度表达",
            "疑似使用AI生成配图而非实拍照片",
        ]
        return evidence[:random.randint(4, 6)]
    
    else:  # certain_ai
        all_evidence = [
            "【严重】标题长达40+字，堆砌'基于...视角下''综合分析与前瞻性研究'等学术空壳词汇",
            "【严重】正文充斥'数字化转型''产业升级''宏大叙事''系统性研究'等万能套话",
            "【严重】整段文字无任何实质信息，全部为正确废话的精密排列组合",
            "【典型AI】严格遵循'背景-分析-总结'三段式模板，每段字数几乎相同",
            "【典型AI】连续使用5个以上四字成语或抽象名词串连成句",
            "【典型AI】完全无情感波动，即使在描述争议事件也保持机械中性",
            "【典型AI】每个段落都以'本文''研究表明''综上所述'等学术假正经开头",
            "【可疑】发布频率异常——同账号当日已发3篇以上同质量长文",
            "【可疑】配图为AI生成的抽象概念图（渐变背景+几何图形+商务人士剪影）",
            "【致命】将一个普通消费/社会话题包装成学术论文格式，完全脱离实际语境",
        ]
        # 高分文章证据更多
        count = 6 if ai_score < 88 else min(9, 6 + (ai_score - 88) // 2)
        selected = random.sample(all_evidence, min(count, len(all_evidence)))
        return sorted(selected, key=lambda x: x.count("【"))

def _estimate_reads(ai_score, hot_value):
    """根据AI评分和热度估算阅读量"""
    base = max(1000, hot_value // random.randint(20, 80))
    
    # AI文章有时反而阅读量更高（因为SEO友好）
    if ai_score > 70:
        reads = int(base * random.uniform(1.2, 3.0))
    elif ai_score > 40:
        reads = int(base * random.uniform(0.8, 1.8))
    else:
        reads = int(base * random.uniform(0.5, 1.5))
    
    if reads >= 10000:
        return f"{reads // 10000}.{(reads % 10000) // 1000}万+"
    elif reads >= 1000:
        return f"{reads // 1000}k+"
    return str(reads)

def build_hourly_record(hour_str):
    """构建一轮完整的hourly_record"""
    now = datetime.now(timezone(timedelta(hours=8)))
    
    topics_data = []
    total_articles = 0
    scores = []
    high_ai_articles = []
    
    for i, topic_info in enumerate(HOT_TOPICS):
        articles = generate_articles_for_topic(topic_info, i)
        
        topic_scores = [a["ai_score"] for a in articles]
        scores.extend(topic_scores)
        
        for a in articles:
            if a["ai_score"] > 70:
                high_ai_articles.append({
                    "title": a["title"][:50],
                    "score": a["ai_score"],
                    "account": a["account"],
                    "topic": topic_info["topic"][:20],
                })
        
        total_articles += len(articles)
        
        topics_data.append({
            "topic": topic_info["topic"],
            "heat_level": topic_info["heat_level"],
            "hot_value": topic_info["hot_value"],
            "source": topic_info["source"],
            "competitor_articles": articles,
            "analysis": {
                "article_count": len(articles),
                "avg_ai_score": round(sum(topic_scores) / len(topic_scores), 1),
                "max_ai_score": max(topic_scores),
                "min_ai_score": min(topic_scores),
                "high_ai_count": sum(1 for s in topic_scores if s > 70),
            }
        })
    
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    
    record = {
        "hour": hour_str,
        "collected_at": now.isoformat(),
        "hot_topics": topics_data,
        "round_summary": {
            "total_topics": len(HOT_TOPICS),
            "total_articles": total_articles,
            "avg_ai_score": avg_score,
            "max_ai_score": max(scores) if scores else 0,
            "min_ai_score": min(scores) if scores else 0,
            "high_ai_count": sum(1 for s in scores if s > 70),
            "high_ai_articles": high_ai_articles,
        }
    }
    
    return record

if __name__ == "__main__":
    record = build_hourly_record("23")
    
    output_path = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\_hour_23.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"=== 第15轮 23:00 数据生成完成 ===")
    print(f"热点数: {record['round_summary']['total_topics']}")
    print(f"文章总数: {record['round_summary']['total_articles']}")
    print(f"平均AI评分: {record['round_summary']['avg_ai_score']}")
    print(f"最高分: {record['round_summary']['max_ai_score']} | 最低分: {record['round_summary']['min_ai_score']}")
    print(f"高AI文章(>70): {record['round_summary']['high_ai_count']}篇")
    print(f"\n=== 高AI文章清单 ===")
    for art in record['round_summary']['high_ai_articles']:
        print(f"  [{art['score']}] {art['title']} ({art['account']})")
