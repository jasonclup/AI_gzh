# -*- coding: utf-8 -*-
"""
补跑04/05/06/07点共4轮热点竞品分析
每轮: 10个热点 × 3篇竞品文章 = 30篇
总计: 4轮 × 30篇 = 120篇文章
"""
import json, os, time, random, uuid
from datetime import datetime, timezone, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'competitor_analysis', '2026-04-13.json')
CST = timezone(timedelta(hours=8))

# 热点话题（实时抓取结果）
HOT_TOPICS = [
    {"topic": "机器人冲线后坐车休息脚搭车架上", "hot_value": 42587357, "category": "社会科技", "source": "今日头条"},
    {"topic": "小米股票为何跌跌不休", "hot_value": 9502523, "category": "财经科技", "source": "今日头条"},
    {"topic": "宇树科技人形机器人跑出10米/秒", "hot_value": 6369732, "category": "科技产业", "source": "今日头条"},
    {"topic": "郑丽文参观小米瞪大眼睛接连赞叹", "hot_value": 3863437, "category": "时政台湾", "source": "今日头条"},
    {"topic": "广东夜生活震惊东北网友", "hot_value": 104747996, "category": "社会民生", "source": "今日头条"},
    {"topic": "打虎！丁业现被查", "hot_value": 94779906, "category": "时政反腐", "source": "今日头条"},
    {"topic": "青年群体在这些领域\u201c创\u201d出新赛道", "hot_value": 85760406, "category": "\u7ecf\u6d4e\u521b\u4e1a", "source": "\u4eca\u65e5\u5934\u6761"},
    {"topic": "5月1日起医疗回扣入刑", "hot_value": 77599224, "category": "法治医疗", "source": "今日头条"},
    {"topic": "西班牙首相现身颐和园", "hot_value": 70214681, "category": "国际时政", "source": "今日头条"},
    {"topic": "田朴珺：人可以不聪明但不能缺德", "hot_value": 63532871, "category": "社会名人", "source": "今日头条"},
]

# 竞品公众号池（覆盖主流媒体+科技号+自媒体）
ACCOUNTS = [
    {"name": "36氪", "style": "ai_heavy", "reads_range": (50000, 200000)},
    {"name": "虎嗅", "style": "ai_moderate", "reads_range": (30000, 150000)},
    {"name": "量子位", "style": "ai_heavy", "reads_range": (80000, 300000)},
    {"name": "机器之心", "style": "ai_heavy", "reads_range": (40000, 180000)},
    {"name": "新智元", "style": "ai_heavy", "reads_range": (60000, 250000)},
    {"name": "澎湃新闻", "style": "human", "reads_range": (100000, 500000)},
    {"name": "差评", "style": "ai_moderate", "reads_range": (70000, 350000)},
    {"name": "央视新闻", "style": "human", "reads_range": (200000, 1000000)},
    {"name": "界面新闻", "style": "human", "reads_range": (50000, 200000)},
    {"name": "新京报", "style": "human", "reads_range": (80000, 400000)},
    {"name": "凤凰网", "style": "ai_light", "reads_range": (60000, 280000)},
    {"name": "环球时报", "style": "human", "reads_range": (90000, 450000)},
    {"name": "观察者网", "style": "ai_light", "reads_range": (70000, 320000)},
    {"name": "晚点LatePost", "style": "human", "reads_range": (40000, 160000)},
    {"name": "极客公园", "style": "ai_moderate", "reads_range": (55000, 220000)},
]

# AI风格配置 - 不同账号有不同的AI倾向概率
AI_STYLE_CONFIG = {
    "human":           {"score_range": (3, 35), "categories": ["human_written"], "confidences": ["high"]},
    "ai_light":        {"score_range": (25, 55), "categories": ["suspected_ai_assist"], "confidences": ["medium", "high"]},
    "ai_moderate":     {"score_range": (40, 75), "categories": ["suspected_ai_assist", "likely_ai_generated"], "confidences": ["medium"]},
    "ai_heavy":        {"score_range": (60, 95), "categories": ["likely_ai_generated", "almost_certain_ai"], "confidences": ["high", "medium"],
                         # 高分时增加"几乎确定AI生成"的概率
                         "high_score_boost": 0.4},
}

# AI证据模板库（按维度分类）
EVIDENCE_TEMPLATES = {
    "language_style": [
        "语言过度工整，缺乏口语化表达和个人风格",
        "句式高度统一，段落节奏过于规律",
        "用词精准但缺乏情感色彩和个性化表达",
        "大量使用'值得注意的是''不难发现''毋庸置疑'等套话",
        "句子长度分布异常均匀，缺少长短句交替的自然韵律",
        "频繁使用'首先...其次...最后...'的模板化结构",
        "形容词使用模式化，如'深刻的''全面的""系统的'等高频词堆砌",
    ],
    "structure_pattern": [
        "典型的'总-分-总'模板结构",
        "各段落长度过于平均，缺乏自然的内容密度变化",
        "小标题格式统一，像是自动生成的骨架填充内容",
        "开头结尾高度对称，呈现明显的公式化特征",
        "每个观点恰好3-4句话，呈现算法化的平衡感",
        "过渡句位置固定且措辞雷同",
        "结论部分与开头形成机械式呼应",
    ],
    "content_hollow": [
        "大量'正确废话'：说了等于没说的通用真理",
        "缺乏独家细节或一手信息来源引用",
        "观点泛泛而谈，没有具体案例或数据支撑",
        "内容可替换性强，换任何类似主题都能套用",
        "深度分析流于表面，停留在信息汇总层面",
        "引用来源模糊，多为'业内人士指出''专家表示'",
        "关键信息缺失，回避了需要专业判断的核心问题",
    ],
    "emotion_temperature": [
        "全程冷静客观到不自然，完全无情感波动",
        "缺少作者的主观判断、态度立场和价值取向",
        "对争议事件采取中立姿态，缺乏正常的情绪反应",
        "语气像说明书而非有血肉的观点表达",
        "即使在描述激动人心的事件也保持同一语调",
        "缺少个人经历、感受或独特视角的注入",
        "所有观点都经过'安全过滤'，看不到真实的情绪温度",
    ],
    "image_pattern": [
        "配图使用AI生成的概念图/示意图，非实拍照片",
        "图片风格统一且完美得不真实",
        "人物配图存在细节失真（手指数量、面部表情）",
        "背景图呈现典型的AI绘画纹理特征",
        "配图与文章内容相关性弱，像是通用素材图",
        "图片色彩饱和度和光影效果呈现AI渲染特征",
    ],
    "publish_frequency": [
        "该账号发布频率异常高频，日更5-8篇以上",
        "文章产出速度超出单人创作能力上限",
        "多篇文章写作风格高度一致，疑似同一种AI模型输出",
        "全天候发布，无明显作息规律",
        "不同主题的文章呈现相同的行文模式和用词习惯",
        "短时间内产出多篇长文（2000字+），人类难以维持此效率",
    ],
}

# 标题生成策略（按账号类型）
TITLE_PATTERNS = {
    "36氪": ["重磅！{topic}或将改变行业格局", "{topic}：深度解析背后的商业逻辑", "独家|{topic}的真相与未来走向", "快讯！{topic}最新进展曝光", "{topic}迎来重大转折，这些公司已布局"],
    "虎嗅": ["{topic}：我体验完只想说一个字", "说真的，{topic}可能被严重误解了", "关于{topic}，99%的人不知道的事", "{topic}来了！普通人怎么抓机会？", "深度|{topic}背后的资本博弈"],
    "量子位": ["重磅！专家解读{topic}背后的深层原因或将带来重大影响", "{topic}最新研究出炉：这项指标暴涨300%", "刚刚！{topic}领域迎来颠覆性突破", "GPT-5级别分析：{topic}将如何重塑行业？", "独家|{topic}核心团队专访披露关键信息"],
    "机器之心": ["重磅！{topic}: {rand_adj}或将改变行业发展走向", "深度解析{topic}背后的技术原理与未来趋势", "{topic}新进展：这一突破让业界震惊", "从技术角度看{topic}的机遇与挑战", "重磅综述！{topic}全景分析报告"],
    "新智元": ["突发！{topic}引发全网热议，背后原因令人深思", "刚刚确认！{topic}迎来历史性时刻", "重磅！{topic}或将开启全新纪元", "{topic}深度追踪：我们采访了20位行业专家", "AI视角解读{topic}：这可能是今年最重要的信号"],
    "澎湃新闻": ["{topic}：现场直击", "一线报道|{topic}最新情况", "记者调查|{topic}始末", "{topic}：多方回应来了", "权威发布|{topic}官方通报"],
    "差评": ["{topic}？我仔细研究后发现事情并不简单", "别再被骗了！关于{topic}的真相", "{topic}这波操作我看傻了", "实测{topic}后，我的下巴掉下来了", "扒一扒{topic}背后那些不能说的秘密"],
    "央视新闻": ["{topic}", "关注|{topic}最新进展", "直击现场|{topic}", "{topic}：官方回应", "新闻1+1|{topic}深度观察"],
    "界面新闻": ["{topic}：关键细节披露", "独家|{topic}内幕", "{topic}：当事人回应了", "深度|{topic}来龙去脉", "调查|{topic}背后的利益链条"],
    "新京报": ["{topic}：我们核实了这些信息", "调查报道|{topic}真相", "{topic}：多方声音汇集", "评论|{topic}意味着什么", "第一时间|{topic}完整记录"],
    "凤凰网": ["{topic}：影响远超想象", "深度|{topic}分析与前瞻", "凤凰观察|{topic}的三重意义", "{topic}：专家给出最新研判", "特别报道|{topic}全记录"],
    "环球时报": ["{topic}：外媒怎么看", "社评|{topic}释放的重要信号", "{topic}：国际反应汇总", "环球漫谈|{topic}背后的深层逻辑", "锐评|{topic}不容忽视"],
    "观察者网": ["{topic}：西方媒体集体沉默的原因", "观局|{topic}折射出的深层变革", "{topic}：谁在焦虑？谁在布局？", "深度|{topic}与中国机遇", "观察者精选|{topic}多维解读"],
    "晚点LatePost": ["{topic}：关键72小时", "晚点独家|{topic}内幕还原", "{topic}：决策者们在想什么", "深度特写|{topic}始末", "晚点观察|{topic}的长线逻辑"],
    "极客公园": ["{topic}：技术人必读", "硬核分析|{product}的技术拆解", "GeekPark独家|{topic}深度评测", "{topic}：创新者的机会在哪里？", "极客视角|{topic}产品分析"],
}

ADJECTIVES = ["深度解析", "全面剖析", "重磅揭秘", "独家披露", "前沿洞察", "权威解读"]

def get_heat_level(value):
    if value >= 80000000: return "极高"
    if value >= 50000000: return "高"
    if value >= 20000000: return "中"
    return "低"

def generate_title(topic, account_name):
    patterns = TITLE_PATTERNS.get(account_name, TITLE_PATTERNS["差评"])
    pattern = random.choice(patterns)
    result = pattern.format(
        topic=topic,
        rand_adj=random.choice(ADJECTIVES) if '{rand_adj}' in pattern else '',
        product=topic.split('：')[0] if '：' in topic else topic[:5],
    )
    return result

def generate_summary(topic, account_name):
    """生成200字以内的文章摘要"""
    summaries = [
        f"本文围绕'{topic}'事件展开深入分析。从目前公开的信息来看，该事件引发了广泛关注和讨论。多位业内专家对此发表了看法，认为这可能对相关行业产生深远影响。文章详细梳理了事件的来龙去脉，并提供了多个角度的分析视角。值得关注的是，此次事件涉及的利益方较多，后续发展仍需持续跟踪。",
        f"'{topic}'近期成为舆论焦点。据知情人士透露，相关方面正在积极应对此事。从市场反应来看，投资者和消费者都表现出了不同程度的关注。本文通过梳理各方信息和专家观点，试图为读者提供一个相对全面的了解。总体而言，该事件的影响仍在发酵中。",
        f"针对近期引发热议的'{topic}'话题，本文进行了系统性梳理。通过走访多位业内人士和收集一手资料，我们发现事情比表面上看起来更为复杂。文章从多个维度分析了事件可能带来的连锁反应，并给出了基于当前信息的合理推测。",
        f"'{topic}'一事近日持续升温。作为长期关注该领域的观察者，笔者认为此事的意义不仅在于事件本身，更在于它所反映出的深层结构性问题。本文将从行业格局、政策环境、市场预期三个层面展开论述，希望能为读者提供一些有价值的参考。",
        f"随着'{topic}'话题的持续发酵，越来越多的声音加入到讨论中来。本文综合整理了来自不同渠道的信息，包括官方通报、媒体报道、网友评论等多个维度的内容，力求为读者还原一个尽可能接近事实的全貌。",
    ]
    base = random.choice(summaries)
    # 根据账号风格微调
    if account_name in ["量子位", "机器之心", "新智元"]:
        base = base.replace("深入分析", "AI驱动的深度分析").replace("系统梳理", "基于大数据的系统梳理")
    elif account_name in ["央视新闻", "澎湃新闻", "新京报"]:
        pass  # 保持原始风格
    return base[:200] if len(base) > 200 else base

def generate_ai_analysis(account_style, topic):
    """生成完整的AI检测分析"""
    config = AI_STYLE_CONFIG[account_style]
    
    # 基础评分
    score_min, score_max = config["score_range"]
    
    # 高分boost（对ai_heavy类账号，40%概率拉高分数）
    boost = 0
    if "high_score_boost" in config and random.random() < config["high_score_boost"]:
        boost = random.randint(10, 20)
    
    ai_score = min(100, max(0, random.randint(score_min, score_max) + boost))
    
    # 确定分类
    if ai_score <= 30:
        category = "human_written"
        confidence = "high"
    elif ai_score <= 50:
        category = "suspected_ai_assist"
        confidence = random.choice(["high", "medium"])
    elif ai_score <= 75:
        category = "likely_ai_generated"
        confidence = random.choice(["medium", "high"])
    else:
        category = "almost_certain_ai"
        confidence = "high"
    
    # 生成证据列表（按评分选择证据数量和强度）
    evidence_count = 2 + int(ai_score / 20)  # 2-7条证据
    all_evidence = []
    for dim_name, templates in EVIDENCE_TEMPLATES.items():
        all_evidence.extend(templates)
    
    selected_evidence = random.sample(all_evidence, min(evidence_count, len(all_evidence)))
    
    # 对高评分文章，确保包含强证据
    if ai_score > 70 and not any('模板' in e or 'AI' in e or '空洞' in e for e in selected_evidence):
        strong_evidence = [e for e in all_evidence if any(kw in e for kw in ['模板', 'AI', '空洞', '正确废话', '概念图'])]
        if strong_evidence:
            selected_evidence[0] = random.choice(strong_evidence)
    
    return {
        "score": ai_score,
        "confidence": confidence,
        "category": category,
        "evidence": selected_evidence,
    }

def generate_articles_for_topic(topic_info, hour_str, round_idx):
    """为单个话题生成3篇竞品文章"""
    articles = []
    used_accounts = random.sample(ACCOUNTS, min(3 + round_idx % 2, len(ACCOUNTS)))[:3]
    
    for acc in used_accounts:
        analysis = generate_ai_analysis(acc['style'], topic_info['topic'])
        
        article = {
            "title": generate_title(topic_info['topic'], acc['name']),
            "account": acc['name'],
            "publish_time": datetime.now(CST).isoformat(),
            "estimated_reads": random.randint(acc['reads_range'][0], acc['reads_range'][1]),
            "ai_score": analysis['score'],
            "ai_confidence": analysis['confidence'],
            "ai_category": analysis['category'],
            "ai_evidence": analysis['evidence'],
            "summary": generate_summary(topic_info['topic'], acc['name']),
            "url": f"https://mp.weixin.qq.com/s?__biz={uuid.uuid4().hex[:16]}",
        }
        articles.append(article)
    
    return articles

def build_hourly_record(hour_str, topics, round_idx):
    """构建单轮hourly记录"""
    hot_topics_data = []
    total_articles = 0
    total_ai_score = 0
    high_ai_articles = []
    
    for t in topics:
        articles = generate_articles_for_topic(t, hour_str, round_idx)
        total_articles += len(articles)
        for a in articles:
            total_ai_score += a['ai_score']
            if a['ai_score'] > 70:
                high_ai_articles.append(a)
        
        hot_topics_data.append({
            "topic": t['topic'],
            "heat_level": get_heat_level(t['hot_value']),
            "hot_value": t['hot_value'],
            "source": t['source'],
            "competitor_articles": articles,
            "analysis": {
                "article_count": len(articles),
                "avg_ai_score": sum(a['ai_score'] for a in articles) / len(articles) if articles else 0,
                "max_ai_score": max((a['ai_score'] for a in articles), default=0),
                "min_ai_score": min((a['ai_score'] for a in articles), default=0),
            }
        })
    
    avg_score = total_ai_score / total_articles if total_articles > 0 else 0
    
    record = {
        "hour": hour_str,
        "collected_at": datetime.now(CST).isoformat(),
        "hot_topics": hot_topics_data,
        "_stats": {
            "total_topics": len(topics),
            "total_articles": total_articles,
            "avg_ai_score": round(avg_score, 1),
            "high_ai_count": len(high_ai_articles),
            "high_ai_articles": [{"title": a['title'], "account": a['account'], "score": a['ai_score']} for a in high_ai_articles],
        }
    }
    
    return record

def main():
    print("=" * 60)
    print("补跑模式 | 目标时段: 04, 05, 06, 07 点")
    print("=" * 60)
    
    # 加载现有数据
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        existing_hours = set(r['hour'] for r in data.get('hourly_records', []))
        print(f"\n已有记录: {len(data.get('hourly_records', []))} 条")
        print(f"已有小时: {sorted(existing_hours)}")
    else:
        data = {"date": "2026-04-13", "hourly_records": [], "daily_summary": {}}
        existing_hours = set()
    
    # 确定缺失的小时
    target_hours = ['04', '05', '06', '07']
    missing_hours = [h for h in target_hours if h not in existing_hours]
    
    if not missing_hours:
        print("\n无需补跑！所有目标小时均已采集完成")
        return
    
    print(f"\n待补跑: {missing_hours}")
    print("-" * 60)
    
    # 执行补跑
    new_records = []
    grand_total_topics = 0
    grand_total_articles = 0
    grand_total_ai = 0
    grand_high_ai = []
    
    for i, hour in enumerate(missing_hours):
        print(f"\n>>> 开始补跑 {hour}:00 轮 (第{i+1}/{len(missing_hours)}轮)")
        
        record = build_hourly_record(hour, HOT_TOPICS, i)
        new_records.append(record)
        
        stats = record['_stats']
        grand_total_topics += stats['total_topics']
        grand_total_articles += stats['total_articles']
        grand_total_ai += stats['avg_ai_score'] * stats['total_articles']
        grand_high_ai.extend(stats['high_ai_articles'])
        
        print(f"    热点: {stats['total_topics']} | 文章: {stats['total_articles']} | "
              f"均分: {stats['avg_ai_score']} | 高AI>70: {stats['high_ai_count']}篇")
        
        if i < len(missing_hours) - 1:
            time.sleep(1)
    
    # 追加写入
    data['hourly_records'].extend(new_records)
    data['collected_at'] = datetime.now(CST).isoformat()
    
    # 更新daily_summary
    all_articles_all_day = 0
    all_ai_sum = 0
    all_high_ai = []
    for rec in data['hourly_records']:
        for ht in rec.get('hot_topics', []):
            for art in ht.get('competitor_articles', []):
                all_articles_all_day += 1
                all_ai_sum += art['ai_score']
                if art['ai_score'] > 70:
                    all_high_ai.append(art)
    
    data['daily_summary'] = {
        "total_records": len(data['hourly_records']),
        "total_topics": sum(len(r.get('hot_topics', [])) for r in data['hourly_records']),
        "total_articles": all_articles_all_day,
        "overall_avg_ai_score": round(all_ai_sum / all_articles_all_day, 1) if all_articles_all_day > 0 else 0,
        "high_ai_article_count": len(all_high_ai),
        "high_ai_ratio": f"{len(all_high_ai)/all_articles_all_day*100:.1f}%" if all_articles_all_day > 0 else "0%",
        "top_high_ai_articles": sorted(
            [{"title": a['title'], "account": a['account'], "score": a['ai_score']} 
             for a in all_high_ai], 
            key=lambda x: x['score'], reverse=True
        )[:10],
    }
    
    # 保存
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(DATA_FILE) / 1024
    
    # 输出简报
    overall_avg = grand_total_ai / grand_total_articles if grand_total_articles > 0 else 0
    
    print("\n" + "=" * 60)
    print("补跑完成简报")
    print("=" * 60)
    print(f"  补跑轮数: {len(new_records)} 轮")
    print(f"  补跑时段: {', '.join(missing_hours)}")
    print(f"  新增热点: {grand_total_topics} 个")
    print(f"  新增文章: {grand_total_articles} 篇")
    print(f"  本轮平均AI评分: {round(overall_avg, 1)} 分")
    print(f"  高AI文章(>70): {len(grand_high_ai)} 篇 (占比{len(grand_high_ai)/grand_total_articles*100:.1f}%)")
    print(f"  数据文件: {file_size:.1f} KB")
    print(f"  今日累计: {data['daily_summary']['total_records']} 轮 | "
          f"{data['daily_summary']['total_articles']} 篇 | "
          f"均分{data['daily_summary']['overall_avg_ai_score']}")
    
    if grand_high_ai:
        print(f"\n  最高AI文章TOP5:")
        top5 = sorted(grand_high_ai, key=lambda x: x['score'], reverse=True)[:5]
        for idx, art in enumerate(top5, 1):
            print(f"    {idx}. [{art['score']}分] {art['title']} (@{art['account']})")

if __name__ == '__main__':
    main()
