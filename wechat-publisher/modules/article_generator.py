# -*- coding: utf-8 -*-
"""
AI 文章生成模块 v3 — 客观分析版
- 紧扣话题，分析事件背景、经过、影响
- 多风格支持：客观分析 / 深度解读 / 热点评论 / 科普讲解
- 重点内容自动标记（加粗/高亮）
- 无需外部AI API，模板引擎毫秒级响应
"""

import json
import logging
import random
import re
import hashlib
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger('WechatPublisher.ArticleGenerator')

# ──────────────────────────────────────
# 写作风格定义
# ──────────────────────────────────────
WRITING_STYLES = {
    'objective': {
        'name': '📊 客观分析',
        'desc': '中立视角，分析事件来龙去脉，适合新闻类话题',
        'tone': '客观、理性、数据支撑',
    },
    'deep': {
        'name': '🔍 深度解读',
        'desc': '深挖背后逻辑和行业影响，适合科技/商业话题',
        'tone': '深入、专业、有洞察力',
    },
    'hot_commentary': {
        'name': '🔥 热点评论',
        'desc': '犀利点评，有观点有态度，适合争议性话题',
        'tone': '鲜明观点、引发讨论、有感染力',
    },
    'popular_science': {
        'name': '📚 科普讲解',
        'desc': '用通俗语言解释复杂概念，适合技术/科普话题',
        'tone': '通俗易懂、循序渐进、有趣味性',
    },
}


class ArticleGenerator:
    """文章生成器 v3 — 客观分析 + 多风格 + 重点高亮"""

    def __init__(self, config: dict):
        self.config = config
        self.style = config.get('ARTICLE_STYLE', 'objective')
        self.min_paragraphs = config.get('MIN_PARAGRAPHS', 5)
        self.max_paragraphs = config.get('MAX_PARAGRAPHS', 8)

    # ─── 开头模板（按风格分类）───
    OPENING_TEMPLATES = {
        'objective': [
            "近日，「{topic}」引发了广泛关注。作为一个长期关注该领域的人，今天我想从几个角度客观梳理一下这件事的来龙去脉。",
            "「{topic}」——这个话题最近在各大平台持续发酵。抛开情绪化的讨论，我们来看看事实到底是什么样的。",
            "关于{topic}，网络上众说纷纭。今天这篇文章，我想用相对客观的视角，帮大家把这件事理清楚。",
            "{topic}的热度居高不下。在加入讨论之前，不妨先了解一下事情的完整面貌。",
        ],
        'deep': [
            "表面上看，{topic}只是一个普通的热点。但如果我们往深处挖，会发现这背后牵涉到的远比表面上看到的要多得多。",
            "很多人只看到了{topic}的表象。今天这篇文章，我想带大家看看水面之下的东西——那些被忽略的关键细节和深层逻辑。",
            "{topic}不是孤立事件。把它放在更大的行业背景下看，你会发现一些很有意思的规律。",
        ],
        'hot_commentary': [
            "说实话，看到{topic}这个消息的时候，我的第一反应是：终于有人把这事儿捅出来了。",
            "{topic}——这波操作，我只能说：意料之外，情理之中。",
            "关于{topic}，有些话可能不太好听，但我还是想说。因为这件事确实值得认真聊聊。",
        ],
        'popular_science': [
            "最近很多人在聊{topic}，但你真的了解它是什么吗？别急，今天我用最简单的方式给你讲明白。",
            "{topic}听起来很高大上？其实没那么复杂。今天我们就用大白话把这个概念拆解清楚。",
            "如果你对{topic}还一知半解，那这篇文章就是为你准备的。不扯术语，只讲人话。",
        ],
    }

    # ─── 正文段落模板库 ───
    BODY_TEMPLATES = {
        # ====== 事件背景 ======
        'background': {
            'objective': [
                "首先，我们需要了解这件事的基本背景。\n\n**事件起因：** {topic}之所以引发关注，核心在于它触及了一个长期存在但一直未被充分讨论的问题。根据目前公开的信息，这件事最早可以追溯到{time_hint}，当时{early_detail}。\n\n随后事态的发展超出了很多人的预期，逐渐从一个小范围的讨论演变成了全民关注的话题。",
                "让我们先回到事情的开始。\n\n{topic}并非突然出现。事实上，相关的迹象早在{time_hint}就已经显现。当时的{early_detail}，为后续的发展埋下了伏笔。\n\n真正让这件事进入公众视野的，是{trigger_event}这一关键节点。从那一刻起，讨论的规模和深度都发生了质的改变。",
            ],
            'deep': [
                "要理解{topic}的意义，我们必须先把时间线拉长一点看。\n\n表面上的导火索是{trigger_event}，但深层原因要追溯到更早。{time_hint}左右，{early_detail}——这个变化看似不起眼，实际上改变了整个行业的游戏规则。\n\n换句话说，我们现在看到的{topic}，其实是多重因素叠加后的必然结果，而不是偶然事件。",
            ],
            'hot_commentary': [
                "这事说来话长，但我尽量讲清楚。\n\n{topic}能火，根本原因是{core_reason}。之前大家可能觉得这事跟自己没关系，直到{trigger_event}发生——一下子所有人都坐不住了。\n\n说白了，这就是一个积压已久的问题终于爆发了。",
            ],
            'popular_science': [
                "在深入细节之前，我先帮你快速建立一个基本认知。\n\n你可以这样理解{topic}：{simple_analogy}\n\n这个概念最早出现在{time_hint}，最初只是{origin_story}。但随着时间推移，它的重要性越来越明显。",
            ],
        },

        # ====== 事件经过/现状 ======
        'what_happened': {
            'objective': [
                "**具体发生了什么？**\n\n截至目前，{topic}的核心情况可以概括为以下几点：\n\n**第一，** {point_1}\n\n**第二，** {point_2}\n\n**第三，** {point_3}\n\n这些信息主要来自{source_hint}。当然，随着事件的进一步发展，部分细节可能会有更新。",
                "让我们来看看{topic}的具体情况。\n\n根据多方信源交叉验证，目前的局面是这样的：{situation_overview}。\n\n其中最受关注的几个关键点包括：\n• **{key_point_a}**——这一点直接影响了{impact_a}\n• **{key_point_b}**——业内人士普遍认为这意味着{impact_b}\n• **{key_point_c}**——这个发展出乎大多数人的预料",
            ],
            'deep': [
                "现在我们来拆解一下{topic}的具体内容。\n\n大多数人关注的可能是表面现象，比如{surface_fact}。但如果你仔细研究会发现，真正的关键在于{hidden_factor}。\n\n这里有一个容易被忽视的细节：{overlooked_detail}。这个细节为什么重要？因为它揭示了{deep_meaning}",
            ],
            'hot_commentary': [
                "来，直接说重点。\n\n{topic}这事，简单说就是：{simple_summary}\n\n但有意思的是各方的反应：\n- 有人说是{view_a}\n- 也有人认为{view_b}\n- 还有一种说法是{view_c}\n\n谁对谁错？往下看你就明白了。",
            ],
            'popular_science': [
                "好，现在进入正题。{topic}到底是怎么回事？\n\n我们可以把它拆成三个部分来理解：\n\n**1. 它是什么？** {what_is_it}\n\n**2. 它怎么工作的？** {how_it_works}\n\n**3. 为什么重要？** {why_matters}\n\n搞清楚这三个问题，基本上你对这件事就有80%的认知了。",
            ],
        },

        # ====== 分析/解读 ======
        'analysis': {
            'objective': [
                "**为什么会这样？几个关键因素值得注意。**\n\n**因素一：宏观环境的变化。** {macro_factor}。这种大环境的变化，使得{topic}的出现具有了一定的必然性。\n\n**因素二：技术和市场的推动。** 从技术层面来看，{tech_factor}；从市场层面来看，{market_factor}。两者共同作用，加速了事态的发展。\n\n**因素三：用户需求的升级。** {demand_factor}。当需求积累到一定程度，供给端的变革就成了时间问题。",
                "**多角度来看这件事。**\n\n从行业视角看，{topic}标志着{industry_impact}。这是一个值得关注的结构性变化。\n\n从用户视角看，直接影响包括{user_impact}。短期内可能会感到{short_term_feeling}，但从长远看{long_term_outlook}。\n\n从业内人士的反馈来看，{expert_view}。这种判断与公开数据的走向基本一致。",
            ],
            'deep': [
                "这里我要说一个可能不太受欢迎的观点：{topic}的本质其实是{essence_view}。\n\n为什么这么说？有三个层面的理由：\n\n**第一层（表象）：** {layer1}——这是所有人都能看到的。\n\n**第二层（机制）：** {layer2}——这部分需要一定的专业知识才能理解，但一旦理解了，很多事情就豁然开朗了。\n\n**第三层（本质）：** {layer3}——这才是决定性的东西。大部分讨论都停留在前两层，但真正重要的恰恰是这第三层。",
            ],
            'hot_commentary': [
                "说到这儿，我必须说几句可能有点刺耳的话。\n\n{topic}这件事，**最大的问题是{biggest_problem}**。这个问题不是一天两天形成的，而是{problem_history}。\n\n但更让我担心的是{worry_point}。因为如果这个问题不解决，类似的事情还会发生。\n\n不过话说回来，{positive_side}——这也是我愿意花时间写这篇文章的原因。",
            ],
            'popular_science': [
                "到这里你可能会问：这跟我有什么关系？\n\n关系大了。让我用个例子说明：{example_analogy}。\n\n所以你看，{topic}并不是什么遥远的概念。它在潜移默化中影响着{daily_impact}。\n\n理解了这个逻辑，很多看似复杂的现象就不难解释了。",
            ],
        },

        # ====== 影响和展望 ======
        'impact_outlook': {
            'objective': [
                "**接下来会怎样？**\n\n短期来看（1-3个月），预计{short_term_forecast}。需要注意的风险点包括{risk_points}。\n\n中期来看（6-12个月），如果{condition_a}能够实现，那么{mid_term_result}；反之则可能出现{alternative_scenario}。\n\n长期来看，{topic}的影响将主要体现在{long_term_impact_areas}。对于相关行业的从业者来说，现在是时候重新评估自己的策略了。",
                "**这件事带来的影响，可能比你想象的更大。**\n\n**直接影响方面：** {direct_impacts}。这些变化已经在近期有所体现。\n\n**间接影响方面：** 更值得关注的是那些不那么明显的连锁反应。比如{chain_reaction}，以及{second_order_effect}。\n\n**对普通人的启示：** {advice_for_readers}",
            ],
            'deep': [
                "最后说说我的判断。\n\n我认为{topic}是一个{milestone_type}节点。理由如下：\n\n{reason_1}\n\n{reason_2}\n\n{reason_3}\n\n基于以上判断，我的建议是{actionable_advice}。当然，市场永远充满不确定性，保持开放心态、持续观察才是正确的姿态。",
            ],
            'hot_commentary': [
                "最后说几句掏心窝子的话。\n\n{topic}这件事给我的最大感触是{key_takeaway}。\n\n如果你问我怎么看？我觉得{my_verdict}。\n\n不管你同不同意我的观点，有一件事是确定的：这个世界在变，而且变得越来越快。我们能做的，就是保持清醒、独立思考。\n\n欢迎评论区交流，咱们一起讨论。",
            ],
            'popular_science': [
                "总结一下今天的要点：\n\n✅ **要点一：** {summary_1}\n\n✅ **要点二：** {summary_2}\n\n✅ **要点三：** {summary_3}\n\n如果你对{topic}感兴趣，建议下一步可以{next_step_suggestion}。知识这个东西，越学越觉得自己知道得少——但这恰恰是最有趣的地方。\n\n有任何问题欢迎留言，我会挑有代表性的回复。",
            ],
        },
    }

    # ─── 结尾模板 ───
    CLOSING_TEMPLATES = {
        'objective': [
            "以上就是关于{topic}的分析。事件仍在发展中，我们将持续关注后续进展。如果你有不同的看法或补充信息，欢迎在评论区讨论。\n\n— 本文基于公开信息整理，仅供参考",
            "总的来说，{topic}是一个值得持续跟踪的话题。它的意义不仅在于事件本身，更在于它所反映出的趋势变化。\n\n感谢阅读。如果你觉得这篇文章有帮助，欢迎转发给同样关注这个话题的朋友。",
        ],
        'deep': [
            "写到这里，我想引用一句话作为结尾：「**{closing_quote}**」\n\n这句话放在{topic}的语境下，格外贴切。希望这篇文章能给你带来一些新的思考角度。\n\n我是{author}，下次见。",
        ],
        'hot_commentary': [
            "好了，今天就聊这么多。\n\n{topic}这事还没完，后续大概率还会有更多动态。关注我，第一时间获取更新。\n\n别忘了点赞评论——你的每一个互动，都是我继续输出的动力。拜拜！👋",
        ],
        'popular_science': [
            "希望这篇文章帮你搞懂了{topic}！\n\n记住：**{key_memory_point}**——这句话概括了今天所有内容的精髓。\n\n还有什么想了解的？告诉我，下期安排！",
        ],
    }

    # ─── 内容填充词库（根据话题关键词智能匹配）───
    CONTENT_FILLERS = {
        # 通用填充
        'time_hints': ['最近几个月', '今年年初', '去年下半年', '本季度以来', '近一段时间'],
        'triggers': ['一则突发消息的曝光', '一家头部企业的官方公告', '权威媒体的深度报道', '行业峰会上的一次发言', '一份研究报告的发布'],
        'sources': ['官方通报、媒体报道和相关企业的公告', '多方信源的交叉验证', '公开披露的信息和业内知情人士的透露'],

        # AI 相关
        'ai_early_details': ['某AI模型在多项基准测试中取得了突破性成绩', '一款新的AI产品开始大规模公测', '一项关于人工智能的重要政策出台', '多家科技公司同时宣布了AI领域的重大投入'],
        'ai_points': [
            '这次的技术突破主要体现在推理能力和多模态处理上，相比上一代有了显著提升',
            '商业化落地的速度超出预期，多个行业已经开始实际应用',
            '开源社区的反应非常活跃，大量开发者涌入生态建设',
        ],

        # 科技/手机
        'tech_early_details': ['一款备受期待的新品正式发布并开启预售', '某科技巨头公布了最新的技术路线图', '一项关键技术取得了专利授权'],
        'tech_points': [
            '新产品的核心卖点集中在性能提升和体验优化两个方面',
            '价格策略相比往年有明显调整，性价比成为主打方向',
            '生态系统进一步完善，跨设备协同能力大幅增强',
        ],

        # 汽车/新能源
        'ev_early_details': ['一家新能源汽车企业发布了全新的产品线', '自动驾驶技术在公开道路测试中取得重要进展', '行业销量数据出现了显著波动'],
        'ev_points': [
            '智能化配置成为新车型的标配，不再只是高端车型的专属',
            '续航里程和充电效率都有了实质性改善',
            '市场竞争格局正在重塑，传统车企和新势力的力量对比发生变化',
        ],

        # 财经/经济
        'finance_early_details': ['一项重大的经济数据发布引起了广泛关注', '某个行业的监管政策发生了重要调整', '资本市场出现了显著的波动'],
        'finance_points': [
            '此次调整影响的范围比预想的更广，涉及多个细分领域',
            '市场参与者的反应呈现出明显的分化态势',
            '长期来看有利于行业的健康发展，但短期阵痛不可避免',
        ],

        # 社会热点
        'social_early_details': ['一件发生在普通人身边的真实故事引发了全网共鸣', '一项社会调查的结果公布后迅速登上热搜', '某个公共政策的新动向成为了舆论焦点'],
        'social_points': [
            '这件事情之所以引起如此大的反响，是因为它触动了很多人的切身利益',
            '不同群体对此事的立场和态度差异较大，反映了社会观念的多元化',
            '相关部门已经注意到舆论的关注，正在积极回应和处理',
        ],
    }

    def generate(self, topic: str, title: str, selected_title: str = None,
                 extra_context: str = "", author_name: str = "AI观察者",
                 style: str = None) -> Dict:
        """生成完整文章"""
        final_title = selected_title or title
        style = style or self.style

        logger.info(f"开始生成文章: {final_title}, 风格: {style}")

        # 根据话题选择内容填充
        fillers = self._get_fillers_for_topic(topic)

        # 构建段落
        paragraphs_data = self._build_paragraphs(topic, final_title, style, fillers, author_name)

        # 为每段添加配图提示和高亮标记
        for i, para in enumerate(paragraphs_data):
            para['image_hint'] = self._generate_image_hint(topic, para['text'], i, len(paragraphs_data))
            para['needs_image'] = i < self.config.get('IMAGES_PER_ARTICLE', 4) and i > 0
            # 提取高亮内容
            para['highlights'] = self._extract_highlights(para['text'])

        result = {
            'title': final_title,
            'original_topic': topic,
            'author': author_name,
            'style': WRITING_STYLES.get(style, WRITING_STYLES['objective'])['name'],
            'paragraphs': paragraphs_data,
            'word_count': sum(len(p['text']) for p in paragraphs_data),
            'created_at': datetime.now().isoformat(),
            'status': 'draft',
            'tags': self._extract_tags(topic),
            'summary': self._generate_summary(paragraphs_data[:3]),
            'cover_image_hint': f"封面图：{topic}相关场景，现代科技风格，竖屏构图",
        }

        logger.info(f"文章生成完成: {final_title}, {len(paragraphs_data)}段, {result['word_count']}字")
        return result

    def _get_content_category(self, topic: str) -> str:
        """判断话题所属的内容类别"""
        topic_lower = topic.lower()
        if any(kw in topic_lower for kw in ['ai', 'gpt', 'chatgpt', 'deepseek', 'kimi', 'claude', '大模型', '人工智能', 'openai']):
            return 'ai'
        elif any(kw in topic_lower for kw in ['苹果', 'apple', '华为', 'huawei', '小米', 'xiaomi', 'iphone', '手机', '折叠屏', '数码']):
            return 'tech'
        elif any(kw in topic_lower for kw in ['特斯拉', 'tesla', 'musk', '自动驾驶', 'fsd', '新能源', 'ev', '汽车', '比亚迪']):
            return 'ev'
        elif any(kw in topic_lower for kw in ['芯片', '英伟达', 'nvidia', '半导体', '算力', 'chip', '台积电']):
            return 'chip'
        elif any(kw in topic_lower for kw in ['股票', '基金', 'A股', '财经', '经济', '利率', '央行', 'GDP', '通胀', '楼市']):
            return 'finance'
        elif any(kw in topic_lower for kw in ['比特币', 'bitcoin', '加密货币', '区块链', 'crypto']):
            return 'crypto'
        else:
            return 'social'

    def _get_fillers_for_topic(self, topic: str) -> Dict:
        """根据话题获取对应的内容填充词"""
        cat = self._get_content_category(topic)
        f = self.CONTENT_FILLERS

        # 通用默认值（所有模板可能引用的键，确保不会 KeyError）
        base = {
            'time_hint': random.choice(f['time_hints']),
            'trigger_event': random.choice(f['triggers']),
            'source_hint': random.choice(f['sources']),
            'core_reason': '这件事触及了大众的切身利益或敏感神经',
            'simple_analogy': '就像智能手机当年取代功能机一样，是一种不可逆的趋势',
            'what_is_it': f'简单来说，{topic}是当前领域中一个非常重要的发展方向',
            'how_it_works': '其核心原理是通过技术创新来解决问题',
            'why_matters': '它正在改变我们的生活方式和工作模式',
            'example_analogy': '想象一下，就像从拨号上网到光纤宽带的变化',
            'daily_impact': '我们日常使用的很多产品和服务',
            # 背景段落用
            'early_detail': f'与{topic}相关的最新动态引发了广泛关注和讨论',
            'origin_story': f'{topic}最初只是一个专业领域的小众话题',
            # 事件经过用
            'situation_overview': f'目前{topic}的整体情况正在持续发展和演变中',
            'key_point_a': '关键进展一：相关各方正在积极应对和调整',
            'key_point_b': '关键进展二：影响范围比预期更广',
            'key_point_c': '关键进展三：后续走向仍需观察',
            'impact_a': '这直接影响了相关行业和从业者的决策方向',
            'impact_b': '这意味着市场格局可能出现新的变化',
            'surface_fact': f'{topic}的表面现象已经引起了广泛注意',
            'hidden_factor': '深层因素往往被大众忽略但更为重要',
            'overlooked_detail': '有一个细节特别值得关注但经常被忽视',
            'deep_meaning': '这背后反映了更深层次的规律和趋势',
            'simple_summary': f'简单来说，{topic}的核心在于它触动了多方利益和关注',
            'view_a': '一种观点认为这是积极的信号',
            'view_b': '另一种观点则持谨慎态度',
            'view_c': '还有观点认为需要更多时间观察',
            # 分析段落用
            'macro_factor': '宏观经济和政策环境正在发生深刻变化',
            'tech_factor': '技术进步为行业发展提供了新的可能性',
            'market_factor': '市场需求和消费习惯也在不断演进',
            'demand_factor': '用户需求升级是推动变化的原动力',
            'essence_view': f'{topic}的本质是时代发展中的一个标志性事件',
            'layer1': '第一层：表象层面的现象已经足够引人注目',
            'layer2': '第二层：机制层面的逻辑值得深入分析',
            'layer3': '第三层：本质层面的规律才是决定性的',
            'biggest_problem': '最大的问题是信息不对称导致认知偏差',
            'problem_history': '这个问题不是一天形成的，而是长期积累的结果',
            'worry_point': '令人担忧的是如果问题不解决可能会产生连锁反应',
            'positive_side': '积极的一面是各方已经开始重视并采取行动',
            # 多角度分析用
            'industry_impact': f'对整个行业而言，{topic}将带来结构性的变化',
            'user_impact': '对普通用户来说，日常体验将受到直接影响',
            'short_term_feeling': '短期内可能会有适应期和不确定性',
            'long_term_outlook': '从长远看，这种变化将推动整体进步',
            'expert_view': '业内人士普遍认为这是一个值得关注的重要信号',
            # 影响展望用
            'direct_impacts': '直接的影响已经开始显现并逐步扩大',
            'chain_reaction': '由此引发的连锁效应正在多个层面展开',
            'second_order_effect': '更深层次的影响将在后续逐步体现出来',
            'advice_for_readers': '建议保持关注、独立思考、理性判断',
            'short_term_forecast': '短期内预计相关讨论和动态将持续活跃',
            'risk_points': '需要注意潜在的不确定性和风险因素',
            'mid_term_result': '中期来看有望看到实质性的进展或变化',
            'alternative_scenario': '另一种可能是进入一段调整或震荡期',
            'long_term_impact_areas': '长远影响将覆盖多个相关领域',
            'milestone_type': '具有里程碑意义的关键节点',
            'reason_1': '第一个理由：基本面因素支持这一判断。',
            'reason_2': '第二个理由：趋势数据提供了有力佐证。',
            'reason_3': '第三个理由：市场反应印证了这一方向。',
            'actionable_advice': '结合自身情况做出理性评估和选择',
            'key_takeaway': f'关于{topic}最重要的启示是保持理性和开放的心态',
            'my_verdict': f'综合来看，{topic}值得关注但不必过度解读',
            # 科普/总结用
            'summary_1': f'要点一：{topic}代表了当前的一个重要发展趋势',
            'summary_2': '要点二：其核心价值在于解决实际问题而非概念炒作',
            'summary_3': '要点三：未来一段时间将是观察和验证的关键窗口',
            'next_step_suggestion': '建议进一步了解相关信息后形成自己的判断',
            'key_memory_point': f'记住一点：{topic}的核心在于实际价值和意义',
            'closing_quote': '唯一不变的是变化本身。',
            'condition_a': '当前的趋势和发展态势得以延续',
            # 点评/评论用
            'core_reason_ext': f'{topic}之所以引发如此大的反响，是因为它触及了普遍关切',
            # 热点评论用
            'point_1': f'从目前已知的各方面信息来看，{topic}涉及的范围比较广泛',
            'point_2': '各方对此事的反应不一，反映出不同立场和视角的差异',
            'point_3': '后续发展仍需持续观察，目前下定论还为时过早',
        }

        if cat == 'ai':
            base.update({
                'early_detail': random.choice(f['ai_early_details']),
                'point_1': random.choice(f['ai_points']),
                'point_2': '相关产业链上下游的企业都在积极布局，投资热度持续攀升',
                'point_3': '监管部门也开始重视这一领域的规范发展，相关政策正在酝酿中',
                'situation_overview': '整个AI行业正处于快速迭代期，技术能力和应用场景都在快速扩展',
                'key_point_a': '大模型的推理能力大幅增强',
                'impact_a': '这使得AI可以处理更复杂的任务，而不只是简单的对话交互',
                'key_point_b': '多模态融合成为主流趋势',
                'impact_b': '文本、图像、语音、视频的统一处理能力正在形成',
                'key_point_c': '落地应用从概念验证转向规模化部署',
                'macro_factor': '全球范围内对AI技术的投入创下新高，各国都将AI上升为国家战略',
                'tech_factor': '算法效率的提升和算力成本的下降，使得先进AI技术的普及成为可能',
                'market_factor': '企业端的需求从尝试探索转向实质采购，付费意愿明显增强',
                'demand_factor': '无论是个人用户还是企业客户，都在寻找通过AI提升效率的方法',
                'surface_fact': '新一代AI模型的能力参数又刷新了纪录',
                'hidden_factor': '真正驱动变化的不是参数规模，而是训练方法和数据质量的双重突破',
                'overlooked_detail': '很多团队开始采用小模型+精调的路线，效果并不输给超大模型',
                'deep_meaning': 'AI发展的范式正在从"堆算力"转向"提效率"',
                'essence_view': '{topic}标志着AI从"能用"到"好用"的关键跨越',
                'layer1': '模型能力更强了——这是显性的',
                'layer2': '成本更低了——这是半显性的',
                'layer3': '开发门槛大幅降低——这才是革命性的，因为它意味着更多人可以参与创新',
                'biggest_problem': '信息不对称——大部分人只看到了 hype，没看到局限',
                'problem_history': '每次新技术浪潮都会经历这样的阶段',
                'worry_point': '过度期待可能导致失望，进而影响合理的投入决策',
                'positive_side': '这次不一样的地方在于，真实的落地案例越来越多',
                'direct_impacts': '相关企业的股价和估值出现明显波动',
                'chain_reaction': '上下游产业链开始同步调整战略',
                'second_order_effect': '人才培养方向和就业市场结构也在悄然变化',
                'advice_for_readers': '保持关注但不盲目跟风，结合自身需求做判断',
                'short_term_forecast': '相关讨论热度将持续，可能会有更多的产品和政策消息公布',
                'risk_points': '技术预期与实际体验之间的落差可能导致舆论反复',
                'mid_term_result': '行业格局初步明朗化',
                'alternative_scenario': '进入一段调整期',
                'long_term_impact_areas': '生产力工具、内容创作、软件开发等多个领域',
                'milestone_type': '重要的里程碑式',
                'reason_1': '技术成熟度曲线显示，我们已经过了期望膨胀期，进入实质落地阶段。',
                'reason_2': '资本和人才的流向表明，这不是一阵风式的炒作。',
                'reason_3': '普通用户已经开始在日常生活中使用相关工具，这是最硬的证明。',
                'actionable_advice': '与其观望，不如找一个小场景亲自试试',
                'key_takeaway': '技术本身不是终点，如何用好技术才是',
                'my_verdict': '值得密切关注，但不要神化也不要妖魔化',
                'summary_1': f'{topic}代表了当前技术发展的一个重要方向',
                'summary_2': '它的核心价值在于解决实际问题，而不是炫技',
                'summary_3': '未来12个月将是关键的观察窗口期',
                'next_step_suggestion': '找一两个感兴趣的应用场景深入了解',
                'key_memory_point': f'{topic}的核心是实用，不是概念',
                'closing_quote': '预测未来的最好方式，就是去创造它。',
                'condition_a': '技术迭代保持当前的节奏',
                'industry_impact': f'{topic}正在重塑整个科技行业的竞争格局和产业分工',
                'user_impact': '普通用户的工作效率和信息获取方式发生了实质性变化',
                'short_term_feeling': '既兴奋又有些不适应',
                'long_term_outlook': 'AI工具将成为像智能手机一样普及的基础设施',
                'expert_view': '业内普遍认为这只是一个开始，更大的变革还在后面',
                'view_a': '这是第四次工业革命的开端',
                'view_b': '不过是又一次技术泡沫罢了',
                'view_c': '有潜力但还需要时间验证',
                'core_reason': 'AI能力已经达到了一个临界点，普通用户也能直观感受到价值',
                'simple_summary': f'关于{topic}，各方观点不一但核心争论点在于它到底能走多远',
            })
        elif cat == 'tech':
            base.update({
                'early_detail': random.choice(f['tech_early_details']),
                'point_1': random.choice(f['tech_points']),
                'point_2': '供应链和产能情况也在逐步改善，此前存在的缺货问题得到缓解',
                'point_3': '软件生态的跟进速度比预期更快，开发者社区的反馈整体正面',
                'situation_overview': f'{topic}所处的消费电子行业正在经历新一轮的产品周期',
                'key_point_a': '硬件规格的全面提升',
                'impact_a': '用户体验得到直观可感知的改善',
                'key_point_b': '价格策略更加务实',
                'impact_b': '覆盖到了更广泛的消费人群',
                'key_point_c': '系统层面的优化和功能创新',
                'macro_factor': '消费电子市场在经历了低迷之后开始回暖',
                'tech_factor': '新材料和新工艺的应用使得产品设计有了更大的发挥空间',
                'market_factor': '消费者换机周期的缩短带来了增量需求',
                'demand_factor': '用户对设备性能和使用体验的要求越来越高',
                'surface_fact': f'{topic}的相关产品在发布会上展示了令人印象深刻的参数',
                'hidden_factor': '真正打动用户的往往不是参数，而是细节体验的打磨',
                'overlooked_detail': '售后服务和生态建设的投入也在加大',
                'deep_meaning': '竞争焦点正在从硬件规格转向综合体验',
                'essence_view': '{topic}反映了消费电子产品从"拼参数"到"拼体验"的转变',
                'biggest_problem': '同质化竞争导致创新乏力',
                'worry_point': '如果创新停滞，市场可能再次陷入存量博弈',
                'positive_side': '这次各家厂商拿出了不少有诚意的产品',
                'direct_impacts': '消费者的购机选择更加丰富',
                'chain_reaction': '供应链上下游同步调整产能和技术方向',
                'second_order_effect': '相关软件和服务生态迎来新的发展机遇',
                'advice_for_readers': '按需购买，不必盲目追新',
                'short_term_forecast': '市场竞争将更加激烈，消费者可能受益于价格战',
                'risk_points': '部分新技术可能还不够成熟，早期用户需要承担一定风险',
                'mid_term_result': '行业格局可能重新洗牌',
                'alternative_scenario': '回归存量博弈、价格战常态化',
                'long_term_impact_areas': '消费电子产品的使用方式和交互逻辑',
                'milestone_type': '行业升级换代的标志性节点',
                'reason_1': '技术创新的积累到了爆发的前夜。',
                'reason_2': '消费者的换机需求经过多年压抑后开始释放。',
                'reason_3': '全球供应链的重构带来了新的竞争机会。',
                'actionable_advice': '关注实际体验而非纸面参数',
                'key_takeaway': '适合自己的才是最好的',
                'my_verdict': '产品不错，但要理性消费',
                'summary_1': f'{topic}代表了当前消费电子领域的一个重要产品迭代',
                'summary_2': '它的核心卖点在于综合体验的提升',
                'summary_3': '未来几个季度将是观察行业走向的关键期',
                'next_step_suggestion': '去线下店实际体验一下再决定',
                'key_memory_point': f'{topic}的价值在于体验提升，不是数字游戏',
                'industry_impact': f'{topic}将推动整个消费电子产业链的技术升级',
                'user_impact': '日常使用设备的体验将有明显改善',
                'short_term_feeling': '期待中带着一丝观望',
                'long_term_outlook': '新一轮换机潮可能即将到来',
                'expert_view': '业内人士普遍看好这一波创新周期',
                'closing_quote': '好产品自己会说话。',
                'condition_a': '各家厂商持续投入研发创新',
                'view_a': '这次终于有诚意了',
                'view_b': '还是换壳不换芯的老套路',
                'view_c': '等等看再说吧',
                'core_reason': f'{topic}触发了消费者对更好产品的渴望',
                'simple_summary': f'{topic}引发了关于消费电子产品发展方向的热议',
            })
        elif cat == 'ev':
            base.update({
                'early_detail': random.choice(f['ev_early_details']),
                'point_1': random.choice(f['ev_points']),
                'point_2': '充电基础设施的建设进度加快，补能便利性持续提升',
                'point_3': '电池技术的进步使得续航焦虑进一步缓解',
                'situation_overview': f'新能源汽车行业正处在从早期 adopter 向 mass market 过渡的关键阶段',
                'key_point_a': '智能化配置的下沉',
                'impact_a': '中低端车型也能享受到高级驾驶辅助功能',
                'key_point_b': '价格战的持续',
                'impact_b': '消费者的购车门槛不断降低',
                'key_point_c': '出海步伐的加快',
                'macro_factor': '全球能源转型的政策导向日益明确',
                'tech_factor': '三电技术（电池电机电控）的成熟度和成本优化达到临界点',
                'market_factor': '油价波动使得电动车的使用成本优势更加凸显',
                'demand_factor': '消费者对新能源汽车的接受度大幅提高',
                'direct_impacts': '传统燃油车市场份额持续下滑',
                'chain_reaction': '加油站、4S店等传统汽车服务行业面临转型压力',
                'second_order_effect': '电力需求和电网负荷结构发生变化',
                'advice_for_readers': '如果有购车计划，建议把电动车纳入考虑范围',
                'short_term_forecast': '价格竞争将更加激烈，消费者选择更加丰富',
                'risk_points': '部分企业的资金链风险和售后服务能力需要关注',
                'mid_term_result': '市场格局初步明朗化，头部效应加剧',
                'alternative_scenario': '进入一轮行业洗牌期',
                'long_term_impact_areas': '出行方式、能源消费、城市规划等多个维度',
                'milestone_type': '交通出行领域的历史性转折',
                'reason_1': '产品力已经可以满足绝大多数日常使用场景。',
                'reason_2': '成本优势在持续扩大。',
                'reason_3': '政策支持和基础设施建设形成了正向循环。',
                'actionable_advice': '根据自己的用车场景做理性评估',
                'key_takeaway': '趋势已定，选对时机是关键',
                'my_verdict': '大势已定，但品牌选择需谨慎',
                'industry_impact': f'{topic}正在重塑整个汽车产业的生态格局',
                'user_impact': '购车决策和使用体验都在发生根本性变化',
                'short_term_feeling': '既兴奋于新功能又担心充电便利性',
                'long_term_outlook': '电动车将成为主流出行工具之一',
                'expert_view': '业内普遍认为2025-2027年是关键窗口期',
                'view_a': '燃油车即将被淘汰',
                'view_b': '电动车还远不成熟',
                'view_c': '两者会长期共存',
                'core_reason': f'{topic}标志着新能源车从政策驱动转向市场驱动',
                'simple_summary': f'关于{topic}，争论焦点在于替代速度和市场格局',
                'summary_1': f'{topic}代表了出行领域的重大变革方向',
                'summary_2': '技术进步和成本下降是核心驱动力',
                'summary_3': '未来3-5年将是格局定型的关键期',
                'next_step_suggestion': '试驾几款不同品牌的车型做对比',
                'key_memory_point': f'{topic}的核心是实用性和经济性的平衡',
                'closing_quote': '未来已经来，只是分布不均匀。',
                'condition_a': '技术迭代和基础设施建设保持当前进度',
                'surface_fact': '各家的销量数据和市场份额变化引人注目',
                'hidden_factor': '真正决定胜负的是智能化能力和服务体系',
                'overlooked_detail': '软件定义汽车的理念正在从概念走向现实',
                'deep_meaning': '汽车正在从交通工具变成智能移动终端',
                'essence_view': '{topic}的本质是出行方式的数字化升级',
                'layer1': '产品形态变了——从机械到智能',
                'layer2': '商业模式变了——从一次性买卖到持续服务',
                'layer3': '用户关系变了——从车主到用户',
                'biggest_problem': '充电基础设施仍不够完善',
                'worry_point': '如果基建跟不上，用户体验会严重拖后腿',
                'positive_side': '各方投入力度空前，问题正在快速改善',
            })
        elif cat == 'finance':
            base.update({
                'early_detail': random.choice(f['finance_early_details']),
                'point_1': random.choice(f['finance_points']),
                'point_2': '市场预期的调整需要一定时间消化，短期内波动可能加剧',
                'point_3': '中长期来看，基本面因素仍然是决定市场走势的根本',
                'situation_overview': f'当前市场对{topic}的反应体现了投资者的分歧',
                'key_point_a': '政策信号的明确程度',
                'impact_a': '直接影响了市场参与者的风险偏好',
                'key_point_b': '资金面的松紧状况',
                'impact_b': '决定了短期内的市场流动性环境',
                'key_point_c': '实体经济数据的走向',
                'macro_factor': '宏观经济周期的阶段性特征正在发生变化',
                'tech_factor': '金融科技的渗透提升了信息透明度和交易效率',
                'market_factor': '投资者结构的机构化趋势愈发明显',
                'demand_factor': '居民理财需求的多样化和专业化',
                'direct_impacts': '资产价格的重新定价',
                'chain_reaction': '相关板块出现联动效应',
                'second_order_effect': '市场情绪和风险偏好的系统性变化',
                'advice_for_readers': '做好资产配置，不要把鸡蛋放在一个篮子里',
                'short_term_forecast': '市场可能维持震荡格局，结构性机会为主',
                'risk_points': '外部不确定性和内部调整压力并存',
                'mid_term_result': '随着基本面明朗化，市场方向将逐渐清晰',
                'alternative_scenario': '如果预期落空可能再次寻底',
                'long_term_impact_areas': '资产配置策略、投资理念、财富管理方式等',
                'milestone_type': '重要的政策或市场拐点',
                'reason_1': '基本面数据开始出现边际改善信号。',
                'reason_2': '估值水平处于历史相对合理区间。',
                'reason_3': '政策面的支持态度比较明确。',
                'actionable_advice': '保持耐心，逢低布局优质标的',
                'key_takeaway': f'{topic}提醒我们：风险管理永远是第一位的',
                'my_verdict': '短期看情绪，长期看基本面',
                'industry_impact': f'{topic}将对多个行业产生连锁影响',
                'user_impact': '普通投资者的资产配置需要相应调整',
                'short_term_feeling': '谨慎观望中带着一丝期待',
                'long_term_outlook': '结构性机会大于系统性风险',
                'expert_view': '机构投资者普遍认为现在是布局期',
                'view_a': '牛市要来了',
                'view_b': '还要跌一阵子',
                'view_c': '震荡市，做波段就好',
                'core_reason': f'{topic}触及了市场的核心关切——信心和预期',
                'simple_summary': f'关于{topic}，多空双方各有论据和逻辑支撑',
                'summary_1': f'{topic}是当前市场最重要的定价因子之一',
                'summary_2': '理解它有助于把握市场的大方向',
                'summary_3': '保持理性和独立思考尤为重要',
                'next_step_suggestion': '回顾历史类似时期的表现作为参考',
                'key_memory_point': f'{topic}的核心启示是敬畏市场、尊重规律',
                'closing_quote': '市场短期是投票机，长期是称重机。',
                'condition_a': '政策和数据保持当前的改善趋势',
                'surface_fact': '指数波动和成交量变化是最直观的表现',
                'hidden_factor': '资金流向的变化往往先于价格反映出来',
                'overlooked_detail': '北向资金的动向值得特别关注',
                'deep_meaning': '这不仅仅是数字游戏，背后是资源的重新分配',
                'essence_view': '{topic}反映了经济转型期的阵痛与机遇',
                'layer1': '表象层面：价格的涨跌',
                'layer2': '机制层面：资金和情绪的博弈',
                'layer3': '本质层面：经济结构和增长模式的调整',
                'biggest_problem': '信息过载导致判断困难',
                'worry_point': '噪音太多容易干扰正确的投资决策',
                'positive_side': '越是混乱的市场，越有机会找到被低估的优质标的',
            })
        elif cat == 'social':
            base.update({
                'early_detail': random.choice(f['social_early_details']),
                'point_1': random.choice(f['social_points']),
                'point_2': '社交媒体上的讨论呈现出多元化的声音，不同的立场都有表达空间',
                'point_3': '此事引发的思考已经超越了事件本身，延伸到更深层次的社会议题',
                'situation_overview': f'{topic}之所以引发广泛共鸣，是因为它折射出了一些普遍性的社会心理',
                'key_point_a': '事件的公共性和普遍关联度',
                'impact_a': '让每个人都能够在其中找到自己的影子',
                'key_point_b': '信息传播的速度和广度',
                'impact_b': '使得讨论迅速从局部扩散到全局',
                'key_point_c': '情感共鸣的力量',
                'macro_factor': '社会发展过程中积累的情绪需要一个出口',
                'tech_factor': '社交平台的算法推荐机制放大了话题的热度',
                'market_factor': '自媒体时代每个参与者都是信息的传播者和解读者',
                'demand_factor': '人们对公平正义和社会进步的渴望从未停止',
                'direct_impacts': '推动了相关问题的关注和讨论',
                'chain_reaction': '引发了更多类似事件的曝光和反思',
                'second_order_effect': '相关政策和管理措施可能会因此调整',
                'advice_for_readers': '理性发声，拒绝网暴',
                'short_term_forecast': '话题热度还会持续一段时间',
                'risk_points': '舆论可能出现极化和反转',
                'mid_term_result': '推动一些实质性的改变',
                'alternative_scenario': '热度消退后一切照旧',
                'long_term_impact_areas': '社会治理、公共讨论环境、媒体生态等',
                'milestone_type': '具有广泛社会意义的公共事件',
                'reason_1': '这件事触动了大众内心深处的某种情感或价值观。',
                'reason_2': '社交媒体的传播放大了事件的影响力。',
                'reason_3': '它提供了一个公共讨论的契机。',
                'actionable_advice': '独立思考，不被情绪裹挟',
                'key_takeaway': f'{topic}的价值在于引发思考和推动改变',
                'my_verdict': '每一件小事都可能推动社会的进步',
                'industry_impact': f'{topic}对相关行业的规范和发展提出了新的要求',
                'user_impact': '每个人的行为模式和认知都可能受到影响',
                'short_term_feeling': '愤怒、同情、无奈等复杂情绪交织',
                'long_term_outlook': '有望推动社会的点滴进步',
                'expert_view': '社会学和传播学专家认为这是研究公共舆论的好案例',
                'view_a': '必须严惩不贷',
                'view_b': '事情没那么简单',
                'view_c': '需要更多事实才能判断',
                'core_reason': f'{topic}击中了社会痛点，引发了普遍共鸣',
                'simple_summary': f'关于{topic}，各方观点交锋激烈但共识也在形成',
                'summary_1': f'{topic}是一个具有广泛社会意义的事件',
                'summary_2': '它揭示了社会中存在的一些深层问题',
                'summary_3': '公众的关注本身就是一种推动力量',
                'next_step_suggestion': '了解更多背景信息，做出独立判断',
                'key_memory_point': f'{topic}的核心价值在于引发思考和促进对话',
                'closing_quote': '阳光是最好的防腐剂。',
                'condition_a': '公众关注度保持在合理范围内并转化为建设性讨论',
                'surface_fact': f'{topic}在各大平台登上热搜榜首',
                'hidden_factor': '每个热搜背后都有更复杂的利益关系和社会背景',
                'overlooked_detail': '普通人在其中发挥的力量不容小觑',
                'deep_meaning': '这是一个关于社会信任和公共参与的话题',
                'essence_view': '{topic}本质上是公众对美好生活的期待和对公平正义的追求',
                'layer1': '事件本身的经过和细节',
                'layer2': '事件背后的社会心理和群体情绪',
                'layer3': '事件所折射出的制度和文化层面的问题',
                'biggest_problem': '信息碎片化导致真相难以还原',
                'worry_point': '情绪化的讨论可能淹没了理性的声音',
                'positive_side': '越来越多的人开始追求事实而非情绪',
            })
        else:
            # 默认通用
            base.update({
                'early_detail': f'与{topic}相关的一系列事件引起了各方的关注和讨论',
                'point_1': f'从目前已知的各方面信息来看，{topic}涉及的范围比较广泛，影响也是多方面的',
                'point_2': '各方对此事的反应不一，反映出不同立场的差异',
                'point_3': '后续发展仍需持续观察，目前下定论还为时过早',
                'key_memory_point': f'保持关注，独立判断',
                'actionable_advice': '多角度看问题，不要急于站队',
                'my_verdict': '让子弹再飞一会儿',
            })

        return base

    def _build_paragraphs(self, topic: str, title: str, style: str,
                          fillers: Dict, author: str) -> List[Dict]:
        """构建完整的段落列表"""
        seed = int(hashlib.md5(f"{topic}{title}{style}{datetime.now().date()}".encode()).hexdigest()[:8], 16)
        random.seed(seed)

        templates = self.BODY_TEMPLATES
        opening_pool = self.OPENING_TEMPLATES.get(style, self.OPENING_TEMPLATES['objective'])
        closing_pool = self.CLOSING_TEMPLATES.get(style, self.CLOSING_TEMPLATES['objective'])

        paragraphs = []

        # 1. 开头
        opening_text = random.choice(opening_pool).format(topic=topic)
        paragraphs.append({
            'type': 'opening',
            'text': opening_text,
        })

        # 2. 事件背景
        bg_templates = templates['background'].get(style, templates['background']['objective'])
        bg_text = random.choice(bg_templates).format(topic=topic, **fillers)
        paragraphs.append({
            'type': 'body',
            'text': bg_text,
        })

        # 3. 事件经过/详情
        what_templates = templates['what_happened'].get(style, templates['what_happened']['objective'])
        what_text = random.choice(what_templates).format(topic=topic, **fillers)
        paragraphs.append({
            'type': 'body',
            'text': what_text,
        })

        # 4. 分析/解读
        analysis_templates = templates['analysis'].get(style, templates['analysis']['objective'])
        analysis_text = random.choice(analysis_templates).format(topic=topic, **fillers)
        paragraphs.append({
            'type': 'body',
            'text': analysis_text,
        })

        # 5. 影响和展望
        impact_templates = templates['impact_outlook'].get(style, templates['impact_outlook']['objective'])
        impact_text = random.choice(impact_templates).format(topic=topic, author=author, **fillers)
        paragraphs.append({
            'type': 'body',
            'text': impact_text,
        })

        # 6. 结尾
        closing_text = random.choice(closing_pool).format(topic=topic, title=title, author=author, **fillers)
        paragraphs.append({
            'type': 'closing',
            'text': closing_text,
        })

        # 添加 index 和 char_count
        for i, p in enumerate(paragraphs):
            p['index'] = i
            p['char_count'] = len(p['text'])

        return paragraphs

    def _extract_highlights(self, text: str) -> List[str]:
        """提取文本中的重点句子（加粗标记的内容）"""
        highlights = []
        # 找到所有 **...** 标记的内容
        bold_matches = re.findall(r'\*\*(.+?)\*\*', text)
        for match in bold_matches:
            if len(match) > 4 and len(match) < 100:  # 合理长度范围
                highlights.append(match)
        return highlights[:5]  # 最多返回5条

    def _generate_image_hint(self, topic: str, text: str, index: int, total: int) -> str:
        """按段落语义生成配图提示 — 核心原则：每段必须不同！"""
        text_clean = re.sub(r'\s+', ' ', text)[:200]
        
        # ── 只从本段文本提取关键词（不混入全局topic，避免所有段相同）──
        known = [
            'GPT', 'ChatGPT', 'OpenAI', 'Claude', 'DeepSeek', 'Sora', 'Kimi',
            '英伟达', 'NVIDIA', '台积电', '芯片', '半导体', '算力', 'GPU',
            '特斯拉', '比亚迪', '自动驾驶', '智驾', '电动车', '新能源',
            '苹果', 'iPhone', '华为', '小米', '折叠屏', 'Vision Pro', 'AR', 'VR',
            'A股', '港股', '美股', '股票', '基金', 'ETF', '比特币', 'BTC',
            'SpaceX', '火箭', '航天', '卫星', '机器人', '人形机器人',
            '大模型', 'AGI', '量子计算', '脑机接口', '固态电池', '鸿蒙',
        ]
        
        # 只在本段文本中找关键词（不加topic）
        kws = []
        lower_text = text_clean.lower()
        for kw in known:
            if kw.lower() in lower_text and kw not in kws:
                kws.append(kw)
        
        # 补充中文短语（只从段落文本提取）
        cn_words = re.findall(r'[\u4e00-\u9fff]{2,6}', text_clean)
        for w in cn_words:
            if w not in kws and not re.match(r'^\d+$', w):
                kws.append(w)
            if len(kws) >= 6:
                break
        
        # 取段落前80字作为场景描述（这是每段独有的）
        para_summary = text_clean[:80] if text_clean else topic
        
        # 按位置给不同场景引导词
        if index == 0:
            scene_type = '新闻开场主视觉'
        elif index >= max(1, total - 2):
            scene_type = '趋势展望与影响'
        else:
            # 中间段落用序号+不同场景描述来区分
            mid_scenes = ['核心技术细节', '行业影响分析', '具体案例场景', '数据对比展示']
            scene_type = mid_scenes[index % len(mid_scenes)]
        
        # 构建精简提示：以段落独有内容为主，topic仅作风格锚定放最后
        kw_str = ' '.join(kws[:8]) if kws else ''
        
        return f"{scene_type} | {para_summary} | {kw_str} | 无人物无面部"

    def _extract_tags(self, topic: str) -> List[str]:
        tags = []
        tag_map = {
            'AI': ['人工智能', '科技'], 'GPT': ['大模型', 'ChatGPT'],
            '芯片': ['半导体', '硬件'], '手机': ['数码', '消费电子'],
            '汽车': ['新能源', '智能出行'], '特斯拉': ['自动驾驶'],
            'DeepSeek': ['开源AI', '国产模型'], '华为': ['鸿蒙', '国产科技'],
            '苹果': ['iPhone', '消费电子'], '股票': ['财经', '投资'],
            '比特币': ['区块链', '加密货币'],
        }
        tags.append('热点资讯')
        for keyword, related in tag_map.items():
            if keyword.lower() in topic.lower():
                tags.extend(related)
        return list(set(tags))[:6]

    def _generate_summary(self, paras: List[Dict]) -> str:
        texts = [p['text'] for p in paras]
        combined = ''.join(texts)
        summary = combined[:150].rstrip()
        if len(combined) > 150:
            summary += '...'
        return summary


    # ──────────────────────────────────────
    # 法律风险检测系统（强制执行）
    # ──────────────────────────────────────
    
    # 红线关键词库（命中则警告或阻断）
    LEGAL_RISK_PATTERNS = {
        # 政治敏感（阻断级）
        'block_political': [
            r'国家领导人[姓名名字]',  # 领导人姓名评价
            r'推翻|颠覆|分裂国家',
            r'台独|藏独|疆独|港独',
            r'法轮功|六四|八九|天安门事件',
            r'颜色革命|和平演变',
        ],
        # 人身权益（需改写）
        'warn_personal': [
            r'(?:曝光|揭露|扒出).*?(?:隐私|私生活|家庭住址|电话号码)',
            r'(?<!据)(?<!网传)(?<!疑似)[^\n]{0,10}(?:肯定是|一定是|绝对是|铁定是)[^\n]{0,10}(?:渣男|绿茶|人渣|骗子|变态)',  # 直接定性评价
            r'(?:死全家|去死|枪毙|千刀万剐)',
        ],
        # 商业法律（需标注）
        'warn_commercial': [
            r'股价.*(?:必涨|必跌|涨停|翻倍|暴涨100%|目标价\d+)',
            r'推荐买入.*?(?:稳赚|无风险|保本收益)',
            r'(?:最好|唯一|第一)(?:强|好|优).*(?:品牌|产品|公司)',
        ],
        # 社会风险（需弱化）
        'warn_social': [
            r'(?:震惊|必看|不看后悔|转给所有人|不转不是中国人)',
            r'(?:全员|所有|一切).*?(?:垃圾|废物|傻X|脑残)',
        ],
    }
    
    # 图片安全约束
    IMAGE_SAFETY_RULES = {
        'forbidden_subjects': [
            'political leader', 'politician', 'flag', 'national emblem',
            'religious symbol', 'weapon', 'gun', 'violence', 'blood',
            'nude', 'sexual', 'horror', 'real person face', 'celebrity portrait',
        ],
        'required_suffix': ', no people, no human, no face, no person, safe for work',
    }

    def legal_check(self, text: str) -> Dict:
        """
        法律安全检查
        返回: {'safe': bool, 'warnings': [], 'blocked': [], 'score': int(0-100)}
        """
        import re
        result = {'safe': True, 'warnings': [], 'blocked': [], 'score': 100}
        
        for category, patterns in self.LEGAL_RISK_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    if category.startswith('block_'):
                        result['blocked'].append({
                            'category': category,
                            'pattern': pattern,
                            'matches': matches[:3],
                        })
                        result['safe'] = False
                        result['score'] -= 30
                    else:
                        result['warnings'].append({
                            'category': category,
                            'pattern': pattern,
                            'matches': matches[:3],
                            'suggestion': self._get_legal_suggestion(category),
                        })
                        result['score'] -= 10
        
        result['score'] = max(0, min(100, result['score']))
        
        if result['blocked']:
            logger.warning(f"法律风险阻断: {len(result['blocked'])}项")
        if result['warnings']:
            logger.info(f"法律风险警告: {len(result['warnings'])}项 (安全分:{result['score']})")
        
        return result

    def _get_legal_suggestion(self, category: str) -> str:
        suggestions = {
            'warn_personal': '改为客观陈述或使用"网友认为/据报道"等第三方表述，删除主观定性词',
            'warn_commercial': '改为"据公开数据显示/有分析认为"，添加"仅供参考不构成投资建议"',
            'warn_social': '删除标题党用词，改为中性描述性标题',
        }
        return suggestions.get(category, '请人工审核此内容')

    def image_safety_check(self, image_hint: str) -> str:
        """为图片生成提示添加安全约束"""
        hint_lower = image_hint.lower()
        for forbidden in self.IMAGE_SAFETY_RULES['forbidden_subjects']:
            if forbidden in hint_lower:
                logger.warning(f"图片安全拦截提示词: {forbidden}")
                image_hint = image_hint.replace(forbidden, '[REMOVED]')
        
        suffix = self.IMAGE_SAFETY_RULES['required_suffix']
        if suffix not in image_hint:
            image_hint = f"{image_hint} {suffix}"
        
        return image_hint

    # ──────────────────────────────────────
    # 人写风格约束系统（目标AI评分<40）
    # ──────────────────────────────────────
    
    # AI高分症状词库（出现频率越高AI评分越高）
    AI_TELLTALE_PATTERNS = {
        # 段落结构类（高权重）
        'structure_risk': [
            (r'^(首先|其次|再次|最后|第一|第二|第三)[，：,:\s]', 8),  # 僵硬序数词
            (r'^(总的来说|综上所述|总而言之|一言以蔽之)', 6),  # 套路总结
            (r'^(值得一提的是|值得注意的是|需要指出的是)', 5),  # 套路引入
        ],
        # 语言特征类
        'language_risk': [
            (r'具有重要意义(?:和深远的影响)?', 4),  # 空洞意义
            (r'引起了广泛关注(?:和讨论)?', 3),  # 泛泛关注
            (r'不容忽视|至关重要|刻不容缓', 3),  # 夸张程度副词
            (r'随着.+?的(?:发展|进步|深入|普及)，', 3),  # 随着句式
            (r'不仅.*?而且.*?同时', 4),  # 递进套话
        },
        # 结尾套路
        'ending_risk': [
            (r'让我们共同期待|让我们拭目以待|让我们携手共进', 8),
            (r'时间会证明一切|历史会给出答案', 5),
            (r'未来已来|未来可期|未来已来分布不均匀', 6),
        ],
    }
    
    # 人写风格增强词库（用于注入）
    HUMAN_STYLE_ENHANCERS = {
        'openings': [
            '说实话，', '讲真，', '我不装了，', '昨天刷到这条消息的时候我愣了一下——',
            '这事儿说起来有点离谱，但确实是真事。', '先说结论：', '你们可能不信，但——',
        ],
        'transitions': [
            '有意思的是，', '但有个细节很多人忽略了——', '说到这儿得插一句，',
            '等等，先别急划走，', '重点来了：', '这里有个反转：',
            '你可能要问，', '我知道有人会说，',
        ],
        'closings': [
            '你怎么看？评论区聊聊。', '这事还没完，后续大概率还有动静。',
            '反正我是这么看的，你不一定同意，但这不重要。',
            '写到这儿突然想到之前XX那件事，感觉挺像的。',
            '好了今天就聊到这儿，下期想看啥？留言告诉我。',
        ],
        'attitude_markers': [
            '我觉得吧，', '我个人倾向认为', '以我的经验来看',
            '这话可能有人不爱听，但', '不怕得罪人说句实话',
            '最让我意外的是', '最讽刺的是', '最搞笑的是',
        ],
    }

    def estimate_ai_score(self, text: str) -> Dict:
        """
        快速估算文本的AI评分（模拟）
        返回: {'estimated_score': 0-100, 'risk_items': [...], 'suggestions': [...]}
        """
        base_score = 50  # 起始分（中等）
        risk_items = []
        suggestions = []
        
        for category, patterns in self.AI_TELLTALE_PATTERNS.items():
            cat_hits = []
            for pattern, weight in patterns:
                matches = re.findall(pattern, text, re.MULTILINE)
                if matches:
                    base_score += weight * len(matches)
                    cat_hits.append({'pattern': pattern[:30], 'count': len(matches), 'weight': weight})
            
            if cat_hits:
                risk_items.append({'category': category, 'items': cat_hits})
        
        # 人写特征加分（降低AI评分）
        human_bonus = 0
        enhancer_categories = self.HUMAN_STYLE_ENHANCERS
        for cat_name, phrases in enhancer_categories.items():
            for phrase in phrases:
                if phrase in text:
                    human_bonus += 3
        
        base_score -= human_bonus
        
        # 文本多样性加分
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            lengths = [len(l) for l in lines]
            variance = (max(lengths) - min(lengths)) / max(max(lengths), 1)
            if variance > 0.7:
                base_score -= 8  # 长度变化大=更人写
            elif variance < 0.3:
                base_score += 5  # 太整齐=更像AI
        
        final_score = max(5, min(95, base_score))
        
        return {
            'estimated_score': round(final_score, 1),
            'risk_items': risk_items,
            'human_features_found': human_bonus // 3,
            'suggestions': suggestions or (
                ['注入更多口语化表达和主观态度' if final_score > 40 else 
                 ['当前风格良好，保持即可']]
            ),
        }

    def apply_human_writing_rules(self, text: str, topic: str = '') -> str:
        """对人写风格规则做后处理"""
        import random
        
        # 1. 随机注入1-2个过渡短语（如果原文太正式）
        formal_indicators = ['首先', '其次', '综上所述', '值得关注的是', '具有重要意义']
        has_formal = any(ind in text for ind in formal_indicators)
        
        if has_formal and random.random() > 0.5:
            enhancer = random.choice(self.HUMAN_STYLE_ENHANCERS['transitions'])
            # 在第二段开头注入
            parts = text.split('\n\n')
            if len(parts) >= 3:
                insert_pos = min(2, len(parts)-1)
                parts[insert_pos] = enhancer + parts[insert_pos]
                text = '\n\n'.join(parts)
        
        # 2. 确保结尾不套路化
        bad_endings = ['让我们共同期待', '让我们拭目以待', '让我们携手共进', '时间会证明一切']
        for bad in bad_endings:
            if bad in text:
                good = random.choice(self.HUMAN_STYLE_ENHANCERS['closings'])
                text = text.replace(bad, good, 1)
        
        # 3. 注入免责声明前缀
        disclaimer = '\n\n---\n*声明：本文基于公开信息整理，仅供参考。文中观点仅代表个人看法，不构成任何投资建议或其他专业意见。部分图片由AI生成。*'
        if '*声明：' not in text:
            text += disclaimer
        
        return text


if __name__ == '__main__':
    import yaml
    import os
    import sys

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    gen = ArticleGenerator(config)
    article = gen.generate(
        topic="78亿变1亿 河南3地曝巨额数据造假",
        title="河南数据造假事件分析",
        selected_title="78亿变1亿：一场数据造假的深度剖析",
        author_name="AI观察者",
        style='objective'
    )
    print(f"\n=== 文章标题 ===\n{article['title']}\n")
    print(f"作者: {article.get('style','')} | {article['word_count']}字 | {len(article['paragraphs'])}段\n")
    for p in article['paragraphs']:
        print(f"\n--- 第{p['index']+1}段 [{p['type']}] ({p['char_count']}字) {'[需配图]' if p.get('needs_image') else ''} ---")
        print(p['text'][:300] + ("..." if len(p['text']) > 300 else ""))
        if p.get('highlights'):
            print(f"   [高亮] {p['highlights']}")
