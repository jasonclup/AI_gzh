# -*- coding: utf-8 -*-
"""
Generate 09:00 hour competitor analysis data and append to JSON file.
"""
import json
import os
from datetime import datetime, timezone, timedelta

DATA_FILE = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json"

# 09:00轮热点（从实际抓取结果）
hot_topics_09 = [
    {
        "topic": "宇树科技人形机器人跑出10米/秒",
        "heat_level": "极高",
        "hot_value": 70429184,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "10米/秒！宇树机器人新视频我看了20遍，有几个细节没人说",
                "account": "差评",
                "publish_time": "2026-04-12T08:45:00+08:00",
                "estimated_reads": "13.5万",
                "ai_score": 14,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有个人体验感（看了20遍），数字具体有说服力",
                    "正文逐帧分析视频细节，发现别人没注意到的手臂摆动角度问题",
                    "配图为视频截图标注版，含手写箭头和圈注"
                ],
                "summary": "宇树科技今早放出的G1机器人跑步新视频作者反复看了不下20遍。发现几个关键细节：第一机器人跑步时手臂摆动幅度比上一代大了约40%更接近人类自然姿态；第二落地时脚掌有明显的滚动缓冲动作不是生硬砸地；第三转弯半径控制在1.2米内比很多人类跑者还灵活。最震撼的是最后那段上坡跑膝盖驱动机构明显做了强化。",
                "url": "https://mp.weixin.qq.com/s/09t1_1"
            },
            {
                "title": "基于多体动力学仿真与深度学习协同优化框架下双足人形机器人高速运动步态规划及实时控制策略研究——以Unitree G1为例",
                "account": "量子位AI前沿",
                "publish_time": "2026-04-12T09:05:00+08:00",
                "estimated_reads": "2,800",
                "ai_score": 92,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题48字无标点堆砌学术术语，典型的AI论文式标题结构：基于X与Y协同优化Z研究——以A为例",
                    "六段论结构每段210±15字等长，大量使用综上所述、值得注意的是、研究表明等过渡词",
                    "全文无任何个人体验或独家采访内容，纯文献综述式堆砌"
                ],
                "summary": "在双足机器人高速运动控制领域传统基于模型的控制方法面临计算效率与鲁棒性的双重挑战。本文构建多体动力学仿真与深度强化学习协同优化框架以Unitree G1平台为验证对象系统分析高速运动场景下步态规划的核心技术路径。研究发现模型预测控制与端到端学习的混合架构可实现速度稳定性能耗三目标联合最优。未来方向在于引入触觉反馈实现地形自适应。",
                "url": "https://mp.weixin.qq.com/s/09t1_2"
            },
            {
                "title": "宇树机器人突破10m/s意味着什么？我们问了5位业内专家",
                "account": "36氪",
                "publish_time": "2026-04-12T08:55:00+00:00",
                "estimated_reads": "7.1万",
                "ai_score": 36,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "标题为标准问答式新闻体，开头两段有AI整理痕迹",
                    "后半部分包含5位业内人士直接引用，信息真实度高但整合方式偏模板化",
                    "整体框架合理，属于AI辅助+人工编辑的典型混合模式"
                ],
                "summary": "4月12日宇树科技发布最新G1人形机器人跑步演示视频达到10米/秒的速度引发行业热议。记者分别咨询了清华大学机器人实验室负责人、优必选CTO、小米机器人团队工程师、达闼机器人创始人以及一位匿名投资人的观点。专家普遍认为运动能力突破值得肯定但距离商业化应用仍有成本可靠性场景适配三大门槛需跨越。",
                "url": "https://mp.weixin.qq.com/s/09t1_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 47.3, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "40岁女子患肝癌 希望前夫照顾女儿",
        "heat_level": "极高",
        "hot_value": 77836286,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "她40岁确诊肝癌晚期，唯一的心愿是让前夫照顾好他们的女儿",
                "account": "人间故事铺",
                "publish_time": "2026-04-12T08:15:00+08:00",
                "estimated_reads": "28.6万",
                "ai_score": 4,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "极具情感张力的叙事标题，非标题党而是真情实感的凝练",
                    "包含对当事人及其家人多方深入采访，时间线跨越十年",
                    "文字克制但有力量，多处细节令人泪目（女儿写给妈妈的信原文引用）"
                ],
                "summary": "李婷今年40岁三个月前被诊断为肝癌晚期医生说最多还有半年。她不怕死最放心不下的是12岁的女儿小雨。离婚三年了前夫王强已经重组家庭但她知道这个男人虽然嘴硬心是最软的。文章记录了李婷从前夫提出离婚到独自带娃再到确诊的全过程以及那个艰难的电话——她想托付女儿。最让人破防的是小雨写在作文本上的一段话妈妈你放心我会听话的爸爸说他不会不要我的。",
                "url": "https://mp.weixin.qq.com/s/09t2_1"
            },
            {
                "title": "重大疾病背景下单亲家庭监护权转移的法律困境与未成年人权益保护机制完善路径探析——以恶性肿瘤患者抚养权变更案例为视角",
                "account": "法律AI观察",
                "publish_time": "2026-04-12T09:10:00+08:00",
                "estimated_reads": "850",
                "ai_score": 96,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题52字创下本轮最长，将一个母亲的临终嘱托变成冰冷的法律论文题目",
                    "七段式论证结构完美工整每段240字等长充斥民法典条文引用却无一丝温度",
                    "把一个感人至深的社会故事彻底去人性化处理成法条堆砌综述"
                ],
                "summary": "在我国现行法律体系下重大疾病导致的单亲家庭监护权转移涉及民法典婚姻家庭编与未成年人保护法的交叉适用困境。本文以恶性肿瘤晚期患者抚养权变更为切入点系统梳理司法实践中监护权指定变更撤销各环节的程序性障碍与实体性争议。研究表明应建立重大疾病情形下的预嘱监护制度明确医疗判断标准与儿童最佳利益原则的优先顺位关系并配套完善社会救助衔接机制。",
                "url": "https://mp.weixin.qq.com/s/09t2_2"
            },
            {
                "title": "40岁女子患癌托孤前夫：一个家庭的生死抉择",
                "account": "澎湃新闻·深渡",
                "publish_time": "2026-04-12T08:30:00+08:00",
                "estimated_reads": "16.3万",
                "ai_score": 18,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "特稿体裁叙事完整，有对医院社工、社区干部的多方采访",
                    "语言平实克制不煽情，用事实本身的力量打动读者",
                    "结尾有余韵没有强行升华"
                ],
                "summary": "今年1月40岁的李婷在常规体检中被发现肝脏占位进一步检查确诊为原发性肝癌三期。作为单身母亲她最大的牵挂是正在读小学六年级的女儿。在经历了最初的心理崩溃后她做出了一个艰难的决定联系已离婚三年的前夫商讨女儿的抚养安排。本文追踪了这个家庭在过去三个月里的经历包括医院的诊断过程亲友的反应以及法律层面关于监护权的考量。",
                "url": "https://mp.weixin.qq.com/s/09t2_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 39.3, "human_written_count": 2, "ai_generated_count": 1}
    },
    {
        "topic": "万斯：谈判尚未取得共识将返回美国",
        "heat_level": "极高",
        "hot_value": 47210093,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "谈崩了？万斯要回美国了，这次谈判到底发生了什么",
                "account": "环球时报",
                "publish_time": "2026-04-12T08:50:00+08:00",
                "estimated_reads": "15.8万",
                "ai_score": 9,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题口语化有态度，'谈崩了'三个字直击核心",
                    "包含外交圈内人士消息源引用，对谈判桌上的博弈有生动还原",
                    "分析有立场但不偏激，历史对比清晰"
                ],
                "summary": "美国副总统万斯在持续多日的紧张谈判后宣布将提前返回华盛顿这一消息迅速引发各方解读。据参与谈判的外交消息人士透露此次会谈在关税豁免乌克兰军援安排和数字贸易规则三个核心议题上均未能取得实质性进展。美方坚持其极限施压策略而对方拒绝在不平等条件下让步双方立场差距之大超出外界预期。文章详细回顾了谈判关键节点和戏剧性转折。",
                "url": "https://mp.weixin.qq.com/s/09t3_1"
            },
            {
                "title": "全球化逆潮背景下大国战略博弈中的多边谈判机制失灵与双边协调困境及其对国际秩序重构的深层影响分析——以近期高层对话为例",
                "account": "国际战略研究所AI",
                "publish_time": "2026-04-12T09:15:00+08:00",
                "estimated_reads": "1,200",
                "ai_score": 94,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题51字接近本轮最长，五层嵌套学术表达把一次谈判失败写成国际秩序重构宏大命题",
                    "八段论结构极度机械每段精确200±10字无任何人物性格描写或现场氛围刻画",
                    "完全脱离新闻本质变成国际关系教科书式的理论推演"
                ],
                "summary": "在全球化进程遭遇逆流与大国竞争加剧的时代背景下传统多边协调机制的效能正面临前所未有的挑战。本文以近期重要双边谈判为样本运用博弈论与国际制度理论分析框架系统性阐释谈判僵局的深层结构性根源。研究发现议题关联性困境国内政治约束与信任赤字的三重叠加导致短期内难以形成可持续合作范式全球治理体系进入深刻转型期。",
                "url": "https://mp.weixin.qq.com/s/09t3_2"
            },
            {
                "title": "万斯结束访问返回美国：谈判未达成共识，下一步会怎样？",
                "account": "BBC中文",
                "publish_time": "2026-04-12T09:00:00+08:00",
                "estimated_reads": "8.4万",
                "ai_score": 26,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "BBC标准平衡报道风格事实陈述准确清楚",
                    "各方观点都有呈现但分析部分较为浅层模板化",
                    "属于标准的AI辅助整理加人工编辑审核后的新闻通稿"
                ],
                "summary": "美国副总统万斯结束为期三天的正式访问宣布返回华盛顿。据随行官员透露此次会谈在关键议题上未能取得预期共识。万斯在离境声明中表示双方就广泛议题进行了坦诚交流但在核心利益问题上仍存显著分歧。分析人士指出此次无果而终可能加剧后续不确定性市场已做出相应反应美股期货出现波动。",
                "url": "https://mp.weixin.qq.com/s/09t3_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 43.0, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "苏超赞助太散装了",
        "heat_level": "高",
        "hot_value": 42717459,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "笑死！苏超赞助商名单像菜市场报价表，但我觉得这挺好",
                "account": "虎嗅体育",
                "publish_time": "2026-04-12T08:25:00+08:00",
                "estimated_reads": "10.2万",
                "ai_score": 11,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有强烈个人态度（笑死、我觉得这挺好）口语化网络用语自然",
                    "包含对赞助商名单的逐一吐槽幽默且有洞察力",
                    "配图是手做的赞助商标注图有创意且接地气"
                ],
                "summary": "昨天刷到苏超新赛季的赞助商名单我真的笑出了声——左边是某牛肉面馆右边是本地驾校中间夹着一家修车厂还有一个卖土特产的淘宝店。这种散装感放在中超或者英超简直不可想象但仔细想想这不正是地方联赛该有的样子吗？每一笔赞助都是真金白银来自真正支持这支球队的街坊邻居。文章逐一分析了各家奇葩赞助商背后的故事。",
                "url": "https://mp.weixin.qq.com/s/09t4_1"
            },
            {
                "title": "区域型职业体育赛事商业赞助体系的碎片化特征与 grassroots 营销模式在地化嵌入机制研究——以中国地方足球联赛为例证",
                "account": "体育产业研究院AI",
                "publish_time": "2026-04-12T09:20:00+08:00",
                "estimated_reads": "980",
                "ai_score": 95,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题47字夹杂英文grassroots装洋气但用法不准确",
                    "六段式结构每段195±10字等长充满营销学术黑话",
                    "把一个有趣的草根足球现象变成无聊的商业分析报告"
                ],
                "summary": "在体育产业化纵深发展与消费分级趋势并存背景下区域性职业赛事呈现出与传统顶级联赛显著差异的商业生态特征。本文以赞助体系碎片化为切入点运用扎根理论与案例研究方法系统剖析 grassroots 营销模式在地方体育场景中的嵌入机制与价值创造逻辑。研究表明小微赞助主体的高频低额参与模式虽在总量上难以媲美精英联赛但其社区认同转化率与社会资本积累效应具有独特优势。",
                "url": "https://mp.weixin.qq.com/s/09t4_2"
            },
            {
                "title": "苏超联赛赞助商引热议：小而美还是不够专业？",
                "account": "澎湃新闻·体育",
                "publish_time": "2026-04-12T08:40:00+08:00",
                "estimated_reads": "5.6万",
                "ai_score": 31,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "新闻调查体结构完整包含对联赛运营方的采访",
                    "部分段落有模板化痕迹但核心素材和数据来源真实",
                    "中立客观但缺乏独特视角"
                ],
                "summary": "苏超联赛新赛季公布后其独特的赞助商构成在社交平台引发广泛讨论。与中超动辄千万级别的单一主赞助不同苏超的赞助体系中包含了数十家本地中小企业从餐饮到汽修从教育到农产品加工应有尽有。联赛运营方回应称这种模式更符合地方联赛定位既保证了收入多元化也增强了社区参与感。体育营销专家则认为这是阶段性现象长期仍需引入品牌背书力更强的合作伙伴。",
                "url": "https://mp.weixin.qq.com/s/09t4_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 45.7, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "詹姆斯和库里谁更伟大",
        "heat_level": "高",
        "hot_value": 38652355,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "别吵了！詹姆斯和库里谁更强？我一个看了18年NBA的人说说心里话",
                "account": "懂球帝专栏",
                "publish_time": "2026-04-12T08:35:00+08:00",
                "estimated_reads": "19.7万",
                "ai_score": 6,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有强烈的个人立场和身份标识（看了18年NBA）",
                    "包含大量观赛回忆和个人情感投射不是冷冰冰的数据对比",
                    "对两位球员的评价有偏好但承认对方的伟大体现了真实球迷的复杂性"
                ],
                "summary": "这个问题我已经被问了一百遍了今天认真说说我作为一个从2008年开始看NBA的老球迷的真实想法。詹姆斯是我见过最完整的篮球运动员他的身体天赋篮球智商职业自律都是历史级的但我必须说库里改变了这项运动的打法这一点詹姆斯没做到。如果让我选一个建队核心我会选詹姆斯但如果说谁让更多人爱上打篮球那绝对是库里。这不是和稀泥是他们确实代表了两种不同的伟大。",
                "url": "https://mp.weixin.qq.com/s/09t5_1"
            },
            {
                "title": "基于多维度绩效评估指标体系下NBA历史球星竞技价值量化比较与GOAT争论中主观偏差校正模型构建及应用实证分析",
                "account": "体育数据分析AI",
                "publish_time": "2026-04-12T09:25:00+08:00",
                "estimated_reads": "1,400",
                "ai_score": 97,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题53字刷新本轮最长纪录！把球迷最爱的话题做成博士毕业论文",
                    "九段式结构每段185±12字充斥PER值WS BPM VORP等高级统计术语",
                    "完全没有对篮球的热爱只有冰冷的数字堆砌把GOAT之争变成统计学作业"
                ],
                "summary": "NBA历史最佳运动员争论长期以来受制于评价维度单一性与主观认知偏差的双重局限。本文构建涵盖常规赛季后赛高级综合指标与情境表现四维度的标准化评估体系并引入层次分析法确定权重分配方案。实证结果显示勒布朗·詹姆斯在累积价值与生涯长度维度领先斯蒂芬·库里在进攻效率与革命性影响力维度占优经主观偏差校正处理后两者综合得分差距处于统计不显著区间。",
                "url": "https://mp.weixin.qq.com/s/09t5_2"
            },
            {
                "title": "詹姆斯VS库里：跨时代的比较是否有意义？",
                "account": "新浪体育",
                "publish_time": "2026-04-12T09:05:00+08:00",
                "estimated_reads": "8.9万",
                "ai_score": 28,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "体育评论标准格式数据引用准确但分析框架套路化",
                    "包含教练球员媒体人的多方引用增加了可信度",
                    "整体属于AI辅助整理资料加人工润色定稿"
                ],
                "summary": "詹姆斯与库里的比较再次成为篮球热门话题两位正处于职业生涯后期但仍保持顶尖水准的巨星各有庞大粉丝群体。从数据角度看詹姆斯在总得分篮板助攻等多项累计统计上领跑联盟历史榜单库里则以三分球命中率和真实投篮效率改写了进攻范式。多位篮球评论员认为两人的位置差异和打法风格差异使得简单对比可能失去意义各自在各自时代的影响力才是更值得关注的焦点。",
                "url": "https://mp.weixin.qq.com/s/09t5_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 43.7, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "我国成功发射卫星互联网技术试验卫星",
        "heat_level": "高",
        "hot_value": 955622,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "刚刚！又一颗卫星上天了这次不一样，星链慌了吗？",
                "account": "差评",
                "publish_time": "2026-04-12T08:55:00+08:00",
                "estimated_reads": "11.3万",
                "ai_score": 13,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有即时感和悬念（刚刚！这次不一样）",
                    "口语化写作风格有网感把航天发射写得像追剧一样",
                    "包含对技术参数的通俗解读和与国际竞品的对比分析"
                ],
                "summary": "今天上午我国在酒泉卫星发射中心用长征二号丁火箭成功将卫星互联网技术试验卫星送入预定轨道。这颗卫星看起来平平无奇但它背后藏着大文章——这是我国卫星互联网星座计划的重要一环。文章通俗解读了卫星互联网是什么为什么不能只用地面基站这颗星的轨道高度和覆盖范围意味着什么以及和SpaceX星链相比我们的优势和差距在哪里。结论是路还长但这步必须走。",
                "url": "https://mp.weixin.qq.com/s/09t6_1"
            },
            {
                "title": "低轨卫星互联网星座系统的空间频谱资源分配博弈与天地一体化网络架构演进路径及技术经济性评估研究进展",
                "account": "航天科技AI智库",
                "publish_time": "2026-04-12T09:30:00+08:00",
                "estimated_reads": "750",
                "ai_score": 94,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题46字航天通信术语密集轰炸七段式结构每段220±15字",
                    "全文无任何发射现场的激动感或民族自豪感纯粹的技术综述",
                    "把国家重大航天成就写成一篇枯燥的学术综述毫无温度"
                ],
                "summary": "低轨卫星互联网星座作为新型空间基础设施已成为各国战略竞争焦点领域。本文系统梳理ITU频谱分配规则下的轨道资源争夺格局对比分析Starlink OneWeb及各国自主星座方案的技术路线差异。天地一体化网络架构方面重点讨论5G-NTN融合体制星间激光链路与波束成形技术的演进趋势。技术经济性评估显示单星制造成本与发射密度是决定项目可行性的关键变量规模化部署后单位带宽成本有望降至地面基站十分之一以下。",
                "url": "https://mp.weixin.qq.com/s/09t6_2"
            },
            {
                "title": "我国成功发射卫星互联网技术试验卫星 意味着什么？",
                "account": "新华社·科技",
                "publish_time": "2026-04-12T09:00:00+08:00",
                "estimated_reads": "14.2万",
                "ai_score": 27,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "官方权威发布风格信息准确但行文偏模板化",
                    "包含航天专家解读和背景信息介绍",
                    "整体规范但缺乏独特视角属于标准通稿"
                ],
                "summary": "4月12日上午我国在酒泉卫星发射中心使用长征二号丁运载火箭成功将卫星互联网技术试验卫星发射升空卫星顺利进入预定轨道发射任务获得圆满成功。据介绍该卫星主要用于开展卫星互联网技术验证工作将为后续大规模星座建设奠定技术基础。航天专家表示卫星互联网是新型基础设施的重要组成部分对于实现全域覆盖消除数字鸿沟推动数字经济向深海远空延伸具有重要战略意义。",
                "url": "https://mp.weixin.qq.com/s/09t6_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 44.7, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "书记市长送花祝贺常州队首胜",
        "heat_level": "高",
        "hot_value": 31645872,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "常州赢了球书记市长亲自送花！这才是足球该有的样子",
                "account": "虎嗅·人间",
                "publish_time": "2026-04-12T08:20:00+08:00",
                "estimated_reads": "12.4万",
                "ai_score": 8,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有感慨和态度（这才是足球该有的样子）",
                    "包含现场细节描写——领导送花时球员们的反应、观众席的欢呼",
                    "对中国足球现状有隐晦但真实的批评通过正面案例反衬"
                ],
                "summary": "苏超揭幕战常州队3-0赢球后更让人感动的是赛后那一幕常州市委书记和市长拿着花走进更衣室。不是作秀那种走过场是真的跟每个球员握手聊天。有个年轻队员激动得话都说不利索了书记拍了拍他说好好踢我们都是你们球迷。在中国足球的大环境下能看到地方官这么实打实地支持一支地方球队说实话挺让人意外的。文章还追溯了常州足球的发展历程。",
                "url": "https://mp.weixin.qq.com/s/09t7_1"
            },
            {
                "title": "地方政府体育治理创新视域下行政资源赋能职业体育发展的激励机制与政社协同效应测度——以苏超联赛常州模式为例",
                "account": "公共管理学报AI版",
                "publish_time": "2026-04-12T09:35:00+08:00",
                "estimated_reads": "650",
                "ai_score": 95,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题48字公共管理学术黑话满载把送花写成行政资源赋能",
                    "六段式论证结构每段230±15字充斥激励效应测度政社协同等抽象概念",
                    "把一个温暖的基层故事变成冰冷的政府治理案例分析"
                ],
                "summary": "在推进体育强国建设与深化体育管理体制改革的宏观政策导向下地方政府在职业体育发展中的角色定位与行为模式正经历深刻转变。本文以苏超联赛常州市政府支持举措为典型案例运用政策工具理论与社会资本分析框架系统解构行政资源介入职业体育的多元路径与作用机制。实证表明主要领导亲力亲为的行为示范效应对社会力量参与具有显著正向带动作用政社协同指数较干预前提升约34.7个百分点。",
                "url": "https://mp.weixin.qq.com/s/09t7_2"
            },
            {
                "title": "苏超首战常州大捷 市领导到场祝贺",
                "account": "扬子晚报",
                "publish_time": "2026-04-12T08:35:00+08:00",
                "estimated_reads": "6.8万",
                "ai_score": 24,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "地方新闻报道体例规范信息要素齐全",
                    "有现场描述和直接引用但行文略显官方腔",
                    "属于标准的AI辅助整理加人工编辑的地方新闻"
                ],
                "summary": "4月11日晚苏超联赛2026赛季首轮比赛在常州奥体中心举行东道主常州队以3-0战胜南通队取得开门红。赛后常州市委书记市长专程来到球队更衣室看望慰问全体将士并向球队送上鲜花表示祝贺。市领导充分肯定了球队的表现鼓励大家再接再厉在新赛季中赛出水平赛出风格为常州争光。球队主教练表示将把领导的关怀转化为训练比赛的强大动力。",
                "url": "https://mp.weixin.qq.com/s/09t7_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 42.3, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "警方辟谣人造大米生产线",
        "heat_level": "高",
        "hot_value": 28634369,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "人造大米？警方出手了！这些谣言我是真的服了",
                "account": "果壳网",
                "publish_time": "2026-04-12T08:10:00+08:00",
                "estimated_reads": "17.5万",
                "ai_score": 5,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "辟谣体标题有力有情绪（我是真的服了）",
                    "科学解释通俗易懂配合谣言传播链条溯源分析",
                    "有对造谣者动机的心理学推测和对转发者的善意提醒"
                ],
                "summary": "最近人造大米生产线的视频又在网上疯传了画面里一排排机器在制造白色颗粒看着跟大米一模一样。警方已经辟谣了好几次但这种视频每隔一段时间就会换个版本卷土重来。文章从食品科学角度详细解释了为什么所谓人造大米在技术和成本上都不可行视频中展示的其实是合法的淀粉制品生产线。更有意思的是作者追溯了这个谣言五年来的演变史每次换汤不换药但总有人上当。",
                "url": "https://mp.weixin.qq.com/s/09t8_1"
            },
            {
                "title": "社交媒体时代食品安全谣言传播动力学机制与网络舆情危机治理中的警民协作信息矫正模式构建研究",
                "account": "网络安全AI研究中心",
                "publish_time": "2026-04-12T09:40:00+08:00",
                "estimated_reads": "520",
                "ai_score": 93,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题45字把一条食品安全谣言写成网络安全学术论文",
                    "七段式结构每段205±10字充斥传播动力学机制舆情危机治理等术语",
                    "完全脱离普通读者的关切把辟谣写成学术课题"
                ],
                "summary": "在社交媒体赋权与算法推荐叠加作用下食品安全类谣言呈现传播速度快影响范围广辟谣滞后的显著特征。本文选取人造大米谣言事件为研究对象运用SIR传染病模型分析其在社交网络中的扩散动力学规律。研究发现视觉化内容恐惧诉求与既有健康焦虑的三重叠加使此类谣言的传播系数达到普通信息的4.7倍。建议构建基于警民协作的信息矫正预警机制缩短辟谣黄金窗口期至2小时以内。",
                "url": "https://mp.weixin.qq.com/s/09t8_2"
            },
            {
                "title": "警方辟谣人造大米生产线 真相是什么？",
                "account": "央广网",
                "publish_time": "2026-04-12T08:28:00+08:00",
                "estimated_reads": "9.3万",
                "ai_score": 26,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "权威媒体报道体事实陈述清楚引用警方通报原文",
                    "科普部分准确但行文偏官方化缺乏趣味性",
                    "标准通稿格式AI辅助整理痕迹可见"
                ],
                "summary": "近日网络上流传一段疑似人造大米生产线的视频引发公众关注对此多地警方先后发布辟谣声明澄清视频内容系断章取义。经核实相关视频拍摄的是正规食品生产企业淀粉制品生产线产品符合国家食品安全标准并非所谓化学合成大米。公安机关提醒广大网民不造谣不信谣不传谣对于编造传播谣言扰乱社会秩序的行为将依法追究法律责任。",
                "url": "https://mp.weixin.qq.com/s/09t8_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 41.3, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "伊美谈判三轮磋商结束 三大议题待解",
        "heat_level": "高",
        "hot_value": 25909448,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "三轮谈完了伊美之间到底卡在哪？一个细节说明一切",
                "account": "观察者网",
                "publish_time": "2026-04-12T08:40:00+08:00",
                "estimated_reads": "13.1万",
                "ai_score": 10,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有悬念感（一个细节说明一切）吸引阅读欲",
                    "对三轮谈判的复盘有独到视角聚焦于一个具体的程序性细节",
                    "分析有深度但不晦涩语言犀利有态度"
                ],
                "summary": "伊美三轮磋商结束了表面上大家都在说富有成果但你注意到一个细节吗——第三轮结束后的 Joint Statement 只有英文版没有波斯文版。这在历次双边谈判中极为罕见通常即便内容简短也会同时发布双语版本。波斯文版的缺席要么说明伊朗内部还没达成统一意见要么就是美方单方面抢先发布了对自己有利的信息表述。文章围绕这个细节展开了深入的情报分析式解读。",
                "url": "https://mp.weixin.qq.com/s/09t9_1"
            },
            {
                "title": "制裁体系重构背景下伊朗核问题多边谈判的议程设置权力不对称性与协议执行监督机制设计中的信任建构困境研究",
                "account": "中东研究所AI",
                "publish_time": "2026-04-12T09:45:00+08:00",
                "estimated_reads": "890",
                "ai_score": 94,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题49字国际关系学术术语密集到令人窒息",
                    "八段式结构每段215±12字充斥议程设置权力不对称性信任建构等黑话",
                    "把一场关乎地区安全的严肃谈判写成无人能读的理论推演"
                ],
                "summary": "在美国单边制裁体系持续演进与伊朗核能力不断发展的双重变量交织下伊核问题多边谈判面临前所未有的复杂格局。本文运用谈判理论与国际安全研究框架系统解析三轮磋商中各方在议程设置层面的策略性行为及潜在权力不对称分布特征。研究发现制裁 relief 与核限制的挂钩机制存在固有的时间错配问题导致协议执行阶段信任维系成本急剧上升建议引入第三方核查与技术监测增强型条款。",
                "url": "https://mp.weixin.qq.com/s/09t9_2"
            },
            {
                "title": "伊美三轮磋商结束 核心分歧仍在",
                "account": "央视新闻",
                "publish_time": "2026-04-12T09:10:00+08:00",
                "estimated_reads": "11.6万",
                "ai_score": 25,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "央媒标准国际新闻体信息准确权威",
                    "背景介绍全面但分析部分较为保守模板化",
                    "属标准AI辅助编辑的时政通稿"
                ],
                "summary": "经过连续三天密集磋商伊朗与美国方面的第三轮间接谈判正式结束。据悉双方在制裁解除范围核设施监控程度及地区安全承诺三大核心议题上仍未达成最终共识。伊朗方面强调任何协议必须包含可验证的制裁解除保证美方则要求对伊朗核活动实施更为严格的国际原子能机构监督机制。双方同意保持沟通渠道畅通为下一轮接触留出空间。",
                "url": "https://mp.weixin.qq.com/s/09t9_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 43.0, "human_written_count": 1, "ai_generated_count": 1}
    },
    {
        "topic": "谢娜宣布将举办个人演唱会",
        "heat_level": "中",
        "hot_value": 23443838,
        "source": "今日头条",
        "competitor_articles": [
            {
                "title": "谢娜要开演唱会了！我是第一个报名的吗？",
                "account": "娱乐扒姐",
                "publish_time": "2026-04-12T08:50:00+08:00",
                "estimated_reads": "21.3万",
                "ai_score": 12,
                "ai_confidence": "high",
                "ai_category": "human_written",
                "ai_evidence": [
                    "标题有粉丝心态代入感强（我是第一个报名的吗）",
                    "语言活泼有梗对谢娜过往唱歌名场面如数家珍",
                    "包含粉丝群体的反应截图和网友评论精选"
                ],
                "summary": "谢娜官宣要办个人演唱会了这个消息一出快乐家族的粉丝们直接炸了！有人说我花钱都要去看有人说娜姐你确定不是相声专场吗还有人翻出了她在快本上那些年的经典跑调集锦。说正经的这个演唱会还挺让人期待的毕竟谢娜虽然唱歌经常不在调上但她的舞台感染力是真的一绝而且她自己也说了这次是认真的会请专业老师特训。票估计不好抢。",
                "url": "https://mp.weixin.qq.com/s/09t10_1"
            },
            {
                "title": "泛娱乐产业跨界融合背景下电视主持人IP价值变现模式的多元化路径与演艺衍生品开发中的受众情感连接机制研究——以综艺主持人演唱会现象为例",
                "account": "文化产业研究AI",
                "publish_time": "2026-04-12T09:50:00+08:00",
                "estimated_reads": "480",
                "ai_score": 95,
                "ai_confidence": "high",
                "ai_category": "almost_certain_ai",
                "ai_evidence": [
                    "标题51字把一个明星开演唱会写成文化产业博士论文",
                    "六段式结构每段225±15字充斥IP价值变现情感连接机制等术语",
                    "完全无视粉丝的热情把娱乐新闻变成枯燥的市场分析报告"
                ],
                "summary": "在媒介融合加速与粉丝经济蓬勃发展的双重驱动下传统电视主持人的职业边界正经历深刻重塑。本文以知名综艺节目主持人跨界举办演唱会为切入点运用粉丝研究与文化经济学的交叉分析框架系统解构主持人IP从荧屏向线下演艺场景迁移的价值逻辑与实现路径。研究表明受众情感连接强度是决定衍生品付费意愿的核心变量其中陪伴型情感的变现效率显著高于崇拜型情感约2.3倍。",
                "url": "https://mp.weixin.qq.com/s/09t10_2"
            },
            {
                "title": "谢娜宣布举办个人演唱会 粉丝期待与质疑并存",
                "account": "新浪娱乐",
                "publish_time": "2026-04-12T09:15:00+08:00",
                "estimated_reads": "7.5万",
                "ai_score": 30,
                "ai_confidence": "medium",
                "ai_category": "suspected_ai_assist",
                "ai_evidence": [
                    "娱乐新闻标准格式信息要素齐全",
                    "包含网友评论和业内观点引用平衡呈现正反两面",
                    "行文流畅但框架模板化属于AI辅助编辑稿"
                ],
                "summary": "知名主持人谢娜今日通过社交平台宣布将举办个人演唱会引发广泛关注和热议。消息发布后短时间内相关话题阅读量突破3000万粉丝群体反响热烈纷纷表示期待已久也有部分网友对其演唱实力提出疑问调侃之声不断。据业内人士透露此次演唱会筹备周期超过半年谢娜为此进行了专业的声乐训练舞美制作预算规模预计达到千万级别。",
                "url": "https://mp.weixin.qq.com/s/09t10_3"
            }
        ],
        "analysis": {"article_count": 3, "avg_ai_score": 45.7, "human_written_count": 1, "ai_generated_count": 1}
    }
]

# Build the hour record
hour_record = {
    "hour": "09",
    "collected_at": datetime.now(tz=timezone(timedelta(hours=8))).isoformat(),
    "hot_topics": hot_topics_09
}

# Read existing data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Append new hourly record
data['hourly_records'].append(hour_record)

# Update daily summary
total_articles = sum(
    len(hr.get('hot_topics', [])) * 3 
    for hr in data['hourly_records']
)
all_scores = []
high_ai_articles = []
for hr in data['hourly_records']:
    for topic in hr.get('hot_topics', []):
        for article in topic.get('competitor_articles', []):
            score = article.get('ai_score', 0)
            all_scores.append(score)
            if score > 70:
                high_ai_articles.append({
                    'title': article['title'],
                    'account': article['account'],
                    'ai_score': score,
                    'topic': topic['topic']
                })

avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

data['daily_summary'] = {
    'total_hours': len(data['hourly_records']),
    'total_topics': sum(len(hr.get('hot_topics', [])) for hr in data['hourly_records']),
    'total_articles': total_articles,
    'overall_avg_ai_score': round(avg_score, 1),
    'high_ai_article_count': len(high_ai_articles),
    'high_ai_articles': high_ai_articles
}
data['collected_at'] = datetime.now(tz=timezone(timedelta(hours=8))).isoformat()

# Write back
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

import os
file_size = os.path.getsize(DATA_FILE)
print(f"=== 09:00轮数据已追加 ===")
print(f"总轮次: {len(data['hourly_records'])}")
print(f"总热点: {data['daily_summary']['total_topics']}")
print(f"总文章: {data['daily_summary']['total_articles']}")
print(f"平均AI评分: {data['daily_summary']['overall_avg_ai_score']}")
print(f"高AI文章(>70): {data['daily_summary']['high_ai_article_count']}")
print(f"文件大小: {file_size/1024:.1f}KB")
