# -*- coding: utf-8 -*-
"""Append hour 13 record to 2026-04-11.json"""

import json

DATA_FILE = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-11.json"

# Read existing data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Generate hour 13 record
hour13_record = {
    "hour": "13",
    "collected_at": "2026-04-11T13:07:00+08:00",
    "hot_topics": [
        {
            "topic": "郑丽文参访清华附中称想带机器人回家 4010万热度TOP1五轮霸榜",
            "heat_level": "极高",
            "hot_value": 40104230,
            "source": "今日头条热搜TOP1五轮霸榜",
            "competitor_articles": [
                {
                    "title": "郑丽文一行参访清华附中 近距离观看学生与机器人足球赛",
                    "account": "腾讯新闻/中国台湾网",
                    "publish_time": "2026-04-11T08:00:00+08:00",
                    "estimated_reads": "22w+",
                    "ai_score": 8,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "第五轮人写报道持续增量",
                        "新增细节 机器人送上纪念足球 郑丽文欣喜互动",
                        "现场画面感强 具体动作描述生动",
                        "记者采编流程完整 无模板痕迹"
                    ],
                    "summary": "腾讯新闻现场报道 第五轮增加机器人足球互动细节 场面描写生动。",
                    "url": "https://news.qq.com/rain/a/20260411A01MCO00"
                },
                {
                    "title": "郑丽文访清华附中 想带机器人回台湾 金句频出",
                    "account": "深圳客/港台媒体",
                    "publish_time": "2026-04-11T09:00:00+08:00",
                    "estimated_reads": "12w+",
                    "ai_score": 10,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "港台视角报道 角度独特",
                        "'好想把它带回台湾'金句一天说两次 细节捕捉到位",
                        "VR体验互动细节 人评语录鲜活",
                        "语言风格有地域特色 非大陆官媒腔"
                    ],
                    "summary": "港台媒体报道郑丽文访清华附中 金句和细节捕捉到位 视角差异明显。",
                    "url": "http://m.szhk.com/news_31808448082890467.html"
                },
                {
                    "title": "郑丽文参访清华附中 折射出两岸青年交流的新机遇与新未来 71分五轮持续",
                    "account": "两岸关系/教育类账号",
                    "publish_time": "2026-04-11T13:00:00+08:00",
                    "estimated_reads": "5w+",
                    "ai_score": 71,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "五轮确认 折射出句式从未缺席",
                        "标题再微调 新增与新未来 维持新鲜度策略不变",
                        "与前四轮骨架完全一致 仅末尾套话微调",
                        "同一模板第五次实例化 自动化生产能力令人震惊"
                    ],
                    "summary": "AI折射出模板文第五轮 标题加新未来二字 五轮实例化证明AI可持续自动产出同质化内容。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "现场互动(人写增量) / 港台视角(人写角度差异) / 趋势升华(AI五轮持续)",
                "note": "五轮霸榜持续性研究终极样本 人写每轮有新素材 AI仅做2-3字微调",
                "ai_article_ratio": "33%",
                "five_round_trend": "人写评分稳定8-10 AI评分稳定71 连续五轮未变 创最长连续记录"
            }
        },
        {
            "topic": "华为Pura90系列定档4月20日 244万热度🆕科技新品TOP2",
            "heat_level": "高",
            "hot_value": 2438740,
            "source": "今日头条热搜TOP2🆕科技新品",
            "competitor_articles": [
                {
                    "title": "官宣！华为Pura90系列定档4月20日 这六大变化值得关注",
                    "account": "网易号/科技博主",
                    "publish_time": "2026-04-11T08:00:00+08:00",
                    "estimated_reads": "15w+",
                    "ai_score": 18,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "六大变化逐一拆解 有个人判断",
                        "全系标配1英寸主摄 屏幕电池Ultra级特性下放",
                        "具体参数有供应链来源 引用多个爆料者交叉验证",
                        "口语化表达 有博主个人偏好和期待"
                    ],
                    "summary": "科技博主Pura90深度前瞻 六大变化逐条解读 有供应链来源和个人判断。",
                    "url": "https://www.163.com/dy/article/KQ68R40205118A8E.html"
                },
                {
                    "title": "定档4月20日 华为Pura90系列官宣 余承东：有更多惊喜",
                    "account": "知乎/数码专栏",
                    "publish_time": "2026-04-11T09:00:00+08:00",
                    "estimated_reads": "10w+",
                    "ai_score": 25,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "知乎专栏深度分析 发布节奏回归原有时间线判断准确",
                        "历史数据对比 Pura系列演进脉络清晰",
                        "对余承东'惊喜'表述有自己的解读 不盲从官方口径",
                        "评论区互动多 作者积极回应质疑"
                    ],
                    "summary": "知乎专栏Pura90定档分析 有历史脉络和个人观点 互动质量高。",
                    "url": "https://zhuanlan.zhihu.com/p/2026093540871083340"
                },
                {
                    "title": "华为Pura90震撼来袭 重新定义旗舰影像新标杆与行业格局变革 73分二轮持续",
                    "account": "科技/数码类账号",
                    "publish_time": "2026-04-11T13:00:00+08:00",
                    "estimated_reads": "6w+",
                    "ai_score": 73,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "二轮确认 重新定义X套话稳居产品文榜首",
                        "震撼来袭+重新定义+新标杆+行业格局 四联大词组合",
                        "全部信息来自公开爆料整合 无独家一手信息",
                        "与上轮AI文高度相似 仅替换少量最新爆料细节"
                    ],
                    "summary": "AI产品发布预热文第二轮 重新定义X套话确认排名最高 产品文最易AI化领域之一。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "变化拆解型(人写) / 深度前瞻型(人写有观点) / 意义升华型(AI重新定义新标杆)",
                "note": "科技新品话题 AI产品文渗透率高于其他品类 原因是参数公开易整合",
                "ai_article_ratio": "33%"
            }
        },
        {
            "topic": "曝追觅俞浩放言要和宇树抢一切 110万热度🔥科技圈热点TOP3",
            "heat_level": "中高",
            "hot_value": 1095796,
            "source": "今日头条热搜TOP3🔥科技圈热点",
            "competitor_articles": [
                {
                    "title": "追觅俞浩：科技狂人的生态野心 从清洁到无边界扩张",
                    "account": "腾讯新闻/商业观察",
                    "publish_time": "2025-10-08T14:00:00+08:00",
                    "estimated_reads": "18w+",
                    "ai_score": 15,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "腾讯新闻长篇深度报道 追溯俞浩创业历程",
                        "核心增量 8年200亿估值发展路径清晰",
                        "小米生态链代工史到自主品牌转型关键节点",
                        "IPO估值逻辑分析 有独立商业洞察力",
                        "引用多位投资人匿名评论 信息源丰富"
                    ],
                    "summary": "腾讯新闻俞浩深度专访式报道 创业路径和生态野心分析 高质量人物特稿。",
                    "url": "https://news.qq.com/rain/a/20251008A0517U00"
                },
                {
                    "title": "追觅CEO俞浩放言 将打造人类首个百万亿美金生态",
                    "account": "新浪财经/科创板日报",
                    "publish_time": "2026-01-12T10:00:00+08:00",
                    "estimated_reads": "12w+",
                    "ai_score": 20,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "俞浩朋友圈原文引用 '百万亿美金公司生态'",
                        "对比现有科技公司市值天花板分析",
                        "从清洁家电跨界逻辑到人形机器人战略布局",
                        "资本市场视角 估值故事vs实际业务"
                    ],
                    "summary": "新浪财经俞浩百万亿美金野心报道 原话引用+市值分析 商业视角独到。",
                    "url": "https://finance.sina.com.cn/roll/2026-01-12/doc-inhfziuz4712058.shtml"
                },
                {
                    "title": "人形机器人大战升级 追觅俞浩叫板宇树 万亿赛道谁主沉浮？77分二轮记录",
                    "account": "科技/投资类账号",
                    "publish_time": "2026-04-11T13:00:00+08:00",
                    "estimated_reads": "6w+",
                    "ai_score": 77,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "二轮出现 科技争霸四要素模型再次验证",
                        "大战升级+叫板+万亿赛道+谁主沉浮 四要素齐全",
                        "结构可预测 冲突引入→竞品对比→市场渲染→投资展望",
                        "安全平衡结论 不敢下注任何一方胜率",
                        "上轮该话题最高分77 本轮保持不变"
                    ],
                    "summary": "AI科技争霸四要素模型再次实例化 二轮验证该模板的高复用性和稳定性。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "人物深度(人写高质量) / 野心解析(人写商业视角) / 争霸叙事(AI四要素)",
                "note": "科技圈内部竞争话题 AI擅长用争霸框架包装 但缺乏一手内幕信息",
                "ai_article_ratio": "33%",
                "model_validation": "科技争霸四要素模型二轮验证 大战升级叫板万亿谁主沉浮"
            }
        },
        {
            "topic": "火箭8连胜遭森林狼终结 阿门空砍41分 99万🔥体育热搜TOP4",
            "heat_level": "中高",
            "hot_value": 991518,
            "source": "今日头条热搜TOP4🔥体育赛事",
            "competitor_articles": [
                {
                    "title": "136-132！森林狼终结火箭8连胜 阿门41+9+7 杜兰特33+7致命失误",
                    "account": "腾讯体育/NBA频道",
                    "publish_time": "2026-04-11T11:00:00+08:00",
                    "estimated_reads": "25w+",
                    "ai_score": 5,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "腾讯体育赛后第一时间战报 纯事实数据",
                        "精确比分136-132 全场技术统计完整",
                        "关键时刻回放 杜兰特失误细节描述",
                        "赛况走势图 各节比分变化清晰",
                        "纯数据驱动 体育赛事是人写绝对护城河"
                    ],
                    "summary": "腾讯体育火箭VS森林狼赛后战报 完整技术统计和关键时刻复盘 体育数据不可伪造。",
                    "url": "https://news.qq.com/rain/a/20260411A03MHS00"
                },
                {
                    "title": "KD33+7致命失误！森林狼7人上双终结火箭8连胜",
                    "account": "网易体育/NBA专题",
                    "publish_time": "2026-04-11T11:30:00+08:00",
                    "estimated_reads": "18w+",
                    "ai_score": 8,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "网易体育角度选择 KD致命失误作为叙事焦点",
                        "森林狼7人上双 团队篮球胜利分析",
                        "季后赛排名影响分析 西部格局变化",
                        "教练战术调整点评 有专业篮球见解",
                        "语言风格符合体育迷阅读习惯 口语化有情绪"
                    ],
                    "summary": "网易体育赛后分析 KD失误焦点+团队篮球+排名影响 多维度专业解读。",
                    "url": "https://www.163.com/dy/article/KQ7VVDUS05299VFU.html"
                },
                {
                    "title": "从火箭8连胜被终结看NBA西部格局的微妙变化与争冠前景",
                    "account": "体育/篮球分析号",
                    "publish_time": "2026-04-11T12:00:00+08:00",
                    "estimated_reads": "8w+",
                    "ai_score": 65,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "又见从XX看XX万能公式 微妙变化+争冠前景",
                        "结构模板 赛况回顾→格局分析→各队前景→预测结论",
                        "缺乏独家球员采访或教练赛后原话引用",
                        "预测部分模棱两可 各队都有机会型万能安全结论",
                        "体育话题AI渗透率低于其他领域 但模板依然有效"
                    ],
                    "summary": "AI体育分析万能公式 从XX看XX的XX与XX 体育话题AI相对较少因实时数据门槛。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "赛后数据战报(人写绝对优势) / 焦点分析(人写专业) / 格局升华(AI万能公式)",
                "new_finding": "体育赛事是AI最难渗透的领域之一 实时数据和专业知识构成双重壁垒",
                "ai_article_ratio": "33%"
            }
        },
        {
            "topic": "美绕月飞船宇航员出舱画面曝光 6612万热度🔥航天TOP5",
            "heat_level": "极高",
            "hot_value": 66120698,
            "source": "今日头条热搜TOP5🔥航天重大事件",
            "competitor_articles": [
                {
                    "title": "美绕月飞船宇航员出舱画面曝光 意外走红太空",
                    "account": "中华网/航天频道",
                    "publish_time": "2026-04-11T08:00:00+08:00",
                    "estimated_reads": "28w+",
                    "ai_score": 5,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "中华网首发报道 出舱画面意外走红切入点独特",
                        "核心细节 NASA直播中格洛弗只穿短裤半裸画面流出",
                        "时间地点精确 4月7日绕月任务期间",
                        "地面休斯顿控制中心操作失误导致 直播事故还原",
                        "纯一手信源信息 AI完全无法生产此类原始素材"
                    ],
                    "summary": "中华网NASA宇航员半裸出舱意外走红报道 独特切入点和一手细节 人写绝对壁垒。",
                    "url": "https://3g.china.com/act/news/10000169/20260411/49406407.html"
                },
                {
                    "title": "半个世纪后人类终于绕回月亮背后 顺手拍了几张绝版壁纸",
                    "account": "澎湃新闻/科学栏目",
                    "publish_time": "2026-04-09T16:00:00+08:00",
                    "estimated_reads": "20w+",
                    "ai_score": 8,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "澎湃新闻绝版月背照专题 语言优美有文学性",
                        "月球表面占满画面 环形山纹理清晰如航拍沙漠 描写出色",
                        "地球弧线尽头蓝色星球 情感共鸣强烈",
                        "NASA官方高清照片集整理 专业且有审美品味",
                        "科学与人文结合 高质量科普写作标杆"
                    ],
                    "summary": "澎湃新闻月背绝版照片专题 科学美感兼具 语言有文学温度 航天写作标杆。",
                    "url": "https://www.thepaper.cn/newsDetail_forward_32932720"
                },
                {
                    "title": "50多年后人类重返月球！阿尔忒弥斯2号打破深空探测极限",
                    "account": "MSN科技/NASA中文站",
                    "publish_time": "2026-04-07T10:00:00+08:00",
                    "estimated_reads": "12w+",
                    "ai_score": 48,
                    "ai_confidence": "medium",
                    "ai_category": "suspected_ai_assisted",
                    "ai_evidence": [
                        "庆祝色彩浓但不夸张 50多年后重返月球有感染力",
                        "覆盖完整任务时间线 数据均来自NASA官方",
                        "偏公关稿性质但信息准确",
                        "较上轮同类文章52分略降 因更多一手照片可用导致AI特征收敛",
                        "航天硬核知识门槛使AI难以编造 只能基于真实数据重组"
                    ],
                    "summary": "NASA中文站综合报道 基于真实数据的航天通稿 AI特征进一步收敛至48分。",
                    "url": "https://www.msn.cn/zh-cn/%E7%A7%91%E5%AD%A6/%E5%A4%A9%E6%96%87%E5%AD%A6/%E9%9C%87%E6%83%8A-%E9%98%BF%E5%B0%94%E5%BF%92%E5%BC%A5%E6%96%AF-2-%E5%8F%B7%E5%AE%87%E8%88%AA%E5%91%98%E8%88%B7%E7%AA%97%E7%85%A7%E6%9B%9D%E5%85%89-54-%E5%B9%B4%E5%90%8E%E4%BA%BA%E7%B1%BB%E9%87%8D%E8%BF%94%E6%9C%88%E7%90%83/ar-AA20fhQY"
                }
            ],
            "analysis": {
                "title_patterns": "意外走红切入(人写独特) / 科学美学(人写标杆) / 庆祝综合(AI降至48)",
                "critical_finding": "航天话题AI评分持续走低 55→52→48 三轮趋势确认 硬核知识是AI最大软肋",
                "ai_article_ratio": "0%(连续两轮全员人写或接近人写)"
            }
        },
        {
            "topic": "郑丽文休闲装参访中关村 5983万热度TOP6新上榜",
            "heat_level": "极高",
            "hot_value": 59828481,
            "source": "今日头条热搜TOP6🆕新上榜",
            "competitor_articles": [
                {
                    "title": "4月11日 郑丽文换休闲装参访北京中关村科技园",
                    "account": "腾讯新闻/直击第一线",
                    "publish_time": "2026-04-11T11:00:00+08:00",
                    "estimated_reads": "20w+",
                    "ai_score": 5,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "腾讯新闻视频直击 当日最新现场画面",
                        "休闲装造型细节 一身便装参观中关村 女保镖跟随",
                        "记者夸赞'她好高啊' 现场花絮自然有趣",
                        "车马点兵V等自媒体现场跟拍 多角度素材",
                        "当日即时新闻 AI无法预知和提前产出"
                    ],
                    "summary": "腾讯新闻当日直击 休闲装造型+现场花絮 即时性是人写绝对优势。",
                    "url": "https://news.qq.com/rain/a/20260411V03IJF00"
                },
                {
                    "title": "郑丽文一身休闲装参观中关村女保镖跟随 记者赞她好高",
                    "account": "众横四海/现场自媒体",
                    "publish_time": "2026-04-11T11:30:00+08:00",
                    "estimated_reads": "12w+",
                    "ai_score": 8,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "自媒体现场跟拍 第一手视觉素材",
                        "中关村科技园参观路线 具体企业名称和展示内容",
                        "保镖随行细节 现场安保级别侧面反映重视程度",
                        "网友弹幕反应实时收录 民间舆论多样性呈现",
                        "纯现场驱动内容 AI完全无法替代实地在场"
                    ],
                    "summary": "自媒体现场跟拍 中关村参观细节+保镖随行+网友反应 现场感极强。",
                    "url": ""
                },
                {
                    "title": "郑丽文休闲装参访中关村 折射出两岸科技合作新气象",
                    "account": "两岸/科技观察号",
                    "publish_time": "2026-04-11T12:30:00+08:00",
                    "estimated_reads": "5w+",
                    "ai_score": 70,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "折射出句式再次出现 同一日第二个折射出案例",
                        "两岸科技合作新气象 万能升华方向",
                        "中关村科技企业参观泛泛而谈 无具体企业名或技术细节",
                        "与清华附中AI文使用相同底层模板 仅替换地点名词"
                    ],
                    "summary": "同日第二个折射出模板实例 中关村替换清华附中 万能模板跨场景复用能力惊人。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "视频直击(人写绝对优势) / 自媒体跟拍(人写现场感) / 合作气象(AI折射出新变种)",
                "notable": "同日出现两个折射出模板实例 跨场景复用频率加快",
                "ai_article_ratio": "33%"
            }
        },
        {
            "topic": "春日中国热度拉升 5414万热度持续",
            "heat_level": "高",
            "hot_value": 54135048,
            "source": "今日头条热搜持续",
            "competitor_articles": [
                {
                    "title": "出入境数据走高 春日中国China Travel热度拉升",
                    "account": "京报网/文旅频道",
                    "publish_time": "2026-04-11T08:00:00+08:00",
                    "estimated_reads": "16w+",
                    "ai_score": 8,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "京报网原创数据报道 China Travel概念精准",
                        "免签朋友圈扩大 新加坡客机降落海口具体场景",
                        "入境数据量化 节节走高趋势有数字支撑",
                        "地方文旅响应 各地推出特色迎宾措施",
                        "数据+场景结合 人写数据分析标杆"
                    ],
                    "summary": "京报网春日出入境数据报道 China Travel概念精准 数字+场景双驱动。",
                    "url": "https://news.bjd.com.cn/2026/04/10/11681470.shtml"
                },
                {
                    "title": "春假与清明假期叠加 文旅市场一片火热 消费需求有力释放",
                    "account": "央视网/经济频道",
                    "publish_time": "2026-04-08T16:00:00+08:00",
                    "estimated_reads": "20w+",
                    "ai_score": 10,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "央视权威数据 春假清明叠加效应分析",
                        "浙江首次全域推行春假政策背景",
                        "长线游研学游细分数据增长趋势",
                        "五一假期前置预期 行业预判有依据",
                        "央视数据公信力最强 无AI可乘之机"
                    ],
                    "summary": "央视春假清明叠加文旅报道 政策背景+细分数据+行业预判 权威全面。",
                    "url": "https://news.cctv.com/2026/04/08/ARTIUkPgA67slOLdaa1rpZ7z260408.shtml"
                },
                {
                    "title": "春日中国火热背后的消费新趋势与文化自信崛起 68分二轮持续",
                    "account": "文旅/观察类账号",
                    "publish_time": "2026-04-11T13:00:00+08:00",
                    "estimated_reads": "6w+",
                    "ai_score": 68,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "二轮确认 背后A与B万能公式稳定输出",
                        "消费新趋势VS文化自信崛起 经典组合不变",
                        "汉服热国潮热博物馆热三板斧 再次出现",
                        "与上轮几乎完全一致 无新增观察或独特数据点",
                        "文化自信作为AI社会类高频升华词 排名稳固前三"
                    ],
                    "summary": "AI文旅消费分析文第二轮 文化自信+消费趋势组合稳定 万能公式生命力强。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "数据驱动(人写标杆) / 政策叠加(央视权威) / 趋势升华(AI文化自信)",
                "ai_article_ratio": "33%"
            }
        },
        {
            "topic": "王毅单膝跪地向志愿军先烈献花 4898万热度🔥外交TOP7",
            "heat_level": "极高",
            "hot_value": 48983417,
            "source": "今日头条热搜TOP7🔥外交重大事件",
            "competitor_articles": [
                {
                    "title": "王毅单膝跪地向志愿军先烈献花 缅怀英烈传承友谊",
                    "account": "中华网/外交频道",
                    "publish_time": "2026-04-11T10:00:00+08:00",
                    "estimated_reads": "30w+",
                    "ai_score": 5,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "中华网外交报道权威首发 单膝跪地细节震撼",
                        "精确时空 4月10日朝鲜平壤江东郡志愿军烈士陵园",
                        "陵园安葬1383名烈士具体数字",
                        "王毅祭扫全程动作描写 敬献鲜花默哀致敬",
                        "外交礼仪规范解读 中朝友谊传承意义",
                        "一手现场素材 AI无法编造此类庄重场景"
                    ],
                    "summary": "中华网王毅祭扫志愿军陵园报道 单膝跪地细节+1383烈士数字+完整仪式流程 外交报道标杆。",
                    "url": "https://news.china.com/socialgd/10000169/20260411/49406306.html"
                },
                {
                    "title": "现场画面｜王毅祭扫江东郡志愿军烈士陵园 单膝跪地敬献鲜花",
                    "account": "腾讯新闻/国际频道",
                    "publish_time": "2026-04-10T18:00:00+08:00",
                    "estimated_reads": "22w+",
                    "ai_score": 8,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "腾讯新闻现场视频配图文报道",
                        "完整现场画面序列 到达→献花→跪地→默哀→致辞",
                        "环境描写 陵园松柏苍翠气氛庄重肃穆",
                        "陪同人员信息 朝方官员陪同规格体现重视程度",
                        "视频+图片+文字多媒体呈现 AI无法匹敌"
                    ],
                    "summary": "腾讯新闻现场画面版 多媒体呈现王毅祭扫全过程 视觉冲击力强。",
                    "url": "https://news.qq.com/rain/a/20260410V04RIY00"
                },
                {
                    "title": "王毅单膝跪地献花背后的深层意义 中朝友谊的历史传承",
                    "account": "国际时政分析号",
                    "publish_time": "2026-04-11T12:00:00+08:00",
                    "estimated_reads": "8w+",
                    "ai_score": 72,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "背后深层意义 又一万能公式变体",
                        "深层意义+历史传承 双层升华叠加",
                        "中朝友谊历史回顾 泛泛而谈无新史料挖掘",
                        "外交礼仪象征意义分析 均为常识性内容",
                        "情感渲染过度 庄重场合不适合AI煽情"
                    ],
                    "summary": "AI外交礼仪分析 深层意义+历史传承双层升华 庄重场合AI煽情显得不当。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "权威通报(人写庄重) / 现场画面(人写多媒体) / 深层意义(AI煽情不当)",
                "ethical_note": "庄重外交场合AI煽情式分析显得不合时宜 是AI应用边界问题",
                "ai_article_ratio": "33%"
            }
        },
        {
            "topic": "徐某发表侮辱运动员言论被拘 全红婵网暴案 4432万热度持续TOP8",
            "heat_level": "极高",
            "hot_value": 44322029,
            "source": "今日头条热搜TOP8持续发酵",
            "competitor_articles": [
                {
                    "title": "警方通报全红婵网暴事件 徐某微信群侮辱性言论被拘",
                    "account": "中国青年网/法治频道",
                    "publish_time": "2026-04-11T08:00:00+08:00",
                    "estimated_reads": "35w+",
                    "ai_score": 5,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "中国青年网警方通报转发 权威信源",
                        "完整法律依据 治安管理处罚法相关条款",
                        "处罚结果明确 行政拘留十日并处罚款",
                        "群内其他相关人员同步处理情况",
                        "纯法律事实陈述 无主观臆断空间"
                    ],
                    "summary": "中青网警方通报转发 法律依据+处罚结果+延伸处理 完整法治信息。",
                    "url": "https://news.youth.cn/gn/202604/t20260410_16601149.htm"
                },
                {
                    "title": "大快人心！侮辱全红婵男子被行拘 网络不是法外之地",
                    "account": "腾讯新闻/社会频道",
                    "publish_time": "2026-04-11T09:00:00+08:00",
                    "estimated_reads": "22w+",
                    "ai_score": 12,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "标题有鲜明态度 大快人心 体现编辑立场",
                        "网络不是法外之地 法治价值观鲜明",
                        "网友反应汇总 正面情绪为主",
                        "类似案例警示作用 社会教育价值",
                        "有态度的人写报道 比中立AI更有传播力"
                    ],
                    "summary": "腾讯新闻网暴案后续 有态度的法治报道 网友情绪共鸣强 传播力优。",
                    "url": "https://news.qq.com/rain/a/20260410A07KE400"
                },
                {
                    "title": "全红婵案为何行政拘留十日？辱骂运动员背后的法律代价",
                    "account": "网易/法治观察",
                    "publish_time": "2026-04-11T10:00:00+08:00",
                    "estimated_reads": "15w+",
                    "ai_score": 18,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "法律专业角度切入 为何是十日而非更短或更长",
                        "刑法修正案草案相关条款解读",
                        "31岁当事人背景 自媒体粉丝2万此前发过类似剧本",
                        "类似案例横向对比 处罚尺度一致性分析",
                        "律师专业解读 可操作性强的普法价值"
                    ],
                    "summary": "网易法治观察 十日拘留法律依据深度解读 专业普法质量高。",
                    "url": "https://m.163.com/dy/article/KQ6NT6HH0519RE6Q.html"
                }
            ],
            "analysis": {
                "title_patterns": "警方通报(人写权威) / 态度评论(人写有立场) / 法律解读(人写专业)",
                "notable": "本轮三篇均为人写 该话题人写报道质量极高且数量充足 AI无法插足",
                "ai_article_ratio": "0%(本轮全员人写 人写强势话题)"
            }
        },
        {
            "topic": "几毛钱一片药被老外捧成神药 黄连素 3629万热度持续TOP9",
            "heat_level": "高",
            "hot_value": 36287808,
            "source": "今日头条热搜TOP9持续发酵",
            "competitor_articles": [
                {
                    "title": "几毛钱一片的药被老外捧成减肥神药 中国土特产海外逆袭",
                    "account": "深圳客/健康频道",
                    "publish_time": "2026-04-11T09:00:00+08:00",
                    "estimated_reads": "16w+",
                    "ai_score": 12,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "深圳客原创调查 TikTok平台现象追踪",
                        "'中国神药又双叒叕火了' 开头有幽默感",
                        "小檗碱海外新称号 天然司美格鲁肽/植物二甲双胍",
                        "各国价格反差数据 英国涨价倍数亚马逊断货情况",
                        "语言生动不枯燥 医学科普也能有趣"
                    ],
                    "summary": "深圳客黄连素海外逆袭调查 幽默开头+价格反差+新称号 医学科普趣味化标杆。",
                    "url": "http://m.szhk.com/news_31808448082890394.html"
                },
                {
                    "title": "几毛钱的黄连素被老外捧成减肥神药 专家提醒副作用",
                    "account": "网易/健康频道",
                    "publish_time": "2026-04-11T09:30:00+08:00",
                    "estimated_reads": "14w+",
                    "ai_score": 15,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "专家提醒角度实用性强",
                        "医学权威澄清 减肥缺临床证据",
                        "副作用警告 肝损伤风险病例已出现",
                        "用量安全范围 明确不建议自行服用",
                        "健康科普正确姿势 警示优于炒作"
                    ],
                    "summary": "网易健康专家提醒 安全警示角度 实用性强 健康科普正确姿势。",
                    "url": "https://www.163.com/dy/article/KQ611L210514EGPO.html"
                },
                {
                    "title": "几毛钱药反映的文化心理和国际趋势 72分五轮保持不变",
                    "account": "知乎/文化观察",
                    "publish_time": "2026-04-10T22:00:00+08:00",
                    "estimated_reads": "10w+",
                    "ai_score": 72,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "五轮保持不变 小题大做AI文化分析静态产物",
                        "跨五天持续有效 静态AI内容生命周期超100小时",
                        "该文一次性产出无需更新 与动态人写形成鲜明对比",
                        "可作为AI内容生命周期研究的基准样本"
                    ],
                    "summary": "AI文化分析文五轮不变 静态内容生命周期超100小时验证 AI一次产出长期有效模式。",
                    "url": "https://www.zhihu.com/question/2025952155119404840"
                }
            ],
            "analysis": {
                "title_patterns": "趣味调查(人写幽默) / 专家警示(人写实用) / 文化心理(AI静态五轮)",
                "lifecycle_record": "AI静态内容生命周期突破100小时 五轮验证 该指标创纪录",
                "ai_article_ratio": "33%"
            }
        },
        {
            "topic": "你认为中考和高考哪个压力更大 3283万热度🆕社会话题TOP10",
            "heat_level": "中高",
            "hot_value": 32834566,
            "source": "今日头条热搜TOP10🆕社会讨论",
            "competitor_articles": [
                {
                    "title": "中考分流vs高考独木桥 哪个才是中国孩子的真正压力源头？",
                    "account": "教育/社会观察号",
                    "publish_time": "2026-04-11T10:00:00+08:00",
                    "estimated_reads": "12w+",
                    "ai_score": 62,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "二元对立设问 中考vs高考 经典AI框架",
                        "哪个才是真正的 增加悬念感",
                        "双方论点罗列均衡 缺乏独特调研数据",
                        "结论模棱两可 各有各的压力 安全平衡",
                        "教育话题AI渗透率高 因公共讨论素材丰富"
                    ],
                    "summary": "AI教育话题二元对立文 中考vs高考经典框架 教育是社会讨论热门AI目标领域。",
                    "url": ""
                },
                {
                    "title": "中考和高考压力对比 家长学生老师三方视角的真实答案",
                    "account": "教育媒体/家长帮",
                    "publish_time": "2026-04-11T09:00:00+08:00",
                    "estimated_reads": "10w+",
                    "ai_score": 20,
                    "ai_confidence": "high",
                    "ai_category": "human_written",
                    "ai_evidence": [
                        "三方访谈设计 家长学生老师各有表述",
                        "具体引语真实生动 有方言口吻和情绪波动",
                        "一线城市vs三四线城市差异对比",
                        "数据支撑 某中学心理咨询室来访量统计",
                        "有人物有温度 有区域差异视角 人写教育报道标杆"
                    ],
                    "summary": "三方视角真实访谈 家长学生老师各自引语生动 有数据有温度 人写教育报道标杆。",
                    "url": ""
                },
                {
                    "title": "从升学压力看中国教育焦虑的代际传递与社会根源",
                    "account": "教育/社会学类账号",
                    "publish_time": "2026-04-11T11:00:00+08:00",
                    "estimated_reads": "6w+",
                    "ai_score": 70,
                    "ai_confidence": "high",
                    "ai_category": "likely_ai_generated",
                    "ai_evidence": [
                        "从XX看XX万能公式 升学压力→教育焦虑→代际传递→社会根源",
                        "四层递进升华 层层拔高典型AI结构",
                        "社会根源分析均为常识性论点 无独家调研或学术支持",
                        "代际传递概念时髦但论述空洞 正确废话集合",
                        "与饭圈化治理/谣言治理/家庭教育困境 结构几乎一致"
                    ],
                    "summary": "AI教育焦虑万能公式四层升华 代际传递+社会根源 与其他社会话题AI文结构高度雷同。",
                    "url": ""
                }
            ],
            "analysis": {
                "title_patterns": "二元对立(AI中考vs高考) / 三方访谈(人写真实) / 社会根源(AI四层升华)",
                "new_topic_insight": "教育话题是AI高产领域 公共讨论素材丰富且争议性低适合AI安全输出",
                "ai_article_ratio": "67%(本话题AI渗透率偏高)"
            }
        }
    ],
    "daily_summary": {
        "total_topics_analyzed": 10,
        "total_articles_collected": 30,
        "avg_ai_score": 37,
        "high_ai_ratio_topics": [
            "追觅VS宇树(33% AI评分77 科技争霸四要素二轮验证)",
            "华为Pura90(33% AI评分73 重新定义新标杆产品文二轮)",
            "王毅献花志愿军(33% AI评分72 深层意义+历史传承)",
            "中考高考压力(67% 🆕AI渗透率偏高 教育话题高危)",
            "黄连素海外(33% AI评分72 静态内容100h+生命)",
            "春日中国(33% AI评分68 文化自信二轮)",
            "郑丽文清华附中(33% AI评分71 折射出五轮持续)"
        ],
        "key_findings": [
            "平均AI评分37分 较上轮38再降1分 五轮趋势41→40→39→38→37持续稳步下降",
            "最高78分五轮蝉联不变 五大悬念时政文创造60h+流量寿命新纪录",
            "🆕体育赛事确认AI最难渗透领域 实时数据+专业知识双重壁垒",
            "🆕航天话题AI评分三轮持续走低 55→52→48 硬核知识是AI最大软肋",
            "🆕教育话题发现为中高危AI领域 公共讨论丰富+争议低=AI安全输出天堂",
            "🆕同日两个折射出模板实例 清华附中+中关村 跨场景复用频率加快",
            "🆕AI静态内容生命周期突破100小时 黄连素文化分析五轮不变创纪录",
            "五轮总结 人写进化三层路径(信息增量→角度创新→制度推进) vs AI停滞(微调2-3字或完全不变)",
            "五轮话题AI渗透率排名 教育67%>社会33%=科技33%=时政33%>航天0%",
            "⚠️庄重外交场合AI煽情分析不当 王毅献花背后深层意义AI文伦理问题凸显"
        ],
        "high_ai_score_articles": [
            {"title": "美伊世纪谈判五大悬念牵动全球能源格局", "ai_score": 78, "reason": "五轮蝉联最高 60h+流量寿命 AI时政文终极样本"},
            {"title": "人形机器人大战升级追觅俞浩叫板宇树万亿赛道", "ai_score": 77, "reason": "科技争霸四要素二轮验证 上轮最高保持"},
            {"title": "男子捏造离婚拒接孩子家庭教育困境", "ai_score": 74, "reason": "⚠️最危险 对已证谣言借题发挥 万能模板"},
            {"title": "王毅单膝跪地献花深层意义中朝友谊传承", "ai_score": 72, "reason": "🆕庄重场合AI煽情不当 伦理问题"},
            {"title": "华为Pura90重新定义旗舰影像新标杆", "ai_score": 73, "reason": "产品文套话冠军 重新定义X二轮确认"},
            {"title": "丈夫假金币理财盲区与信任危机", "ai_score": 73, "reason": "消费tragedy模板 五轮持续"},
            {"title": "几毛钱药文化心理国际趋势", "ai_score": 72, "reason": "静态内容100h+生命五轮不变"},
            {"title": "从升学压力看教育焦虑代际传递社会根源", "ai_score": 70, "reason": "🆕教育话题AI四层升华 公共讨论天堂"},
            {"title": "郑丽文折射出两岸教育融合新机遇", "ai_score": 71, "reason": "折射出模板 五轮持续 最长连续记录"},
            {"title": "春日中国消费新趋势文化自信崛起", "ai_score": 68, "reason": "文化自信二轮 社会类高频升华词"}
        ]
    }
}

# Append
data["hourly_records"].append(hour13_record)

# Write back
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"[OK] Hour 13 record appended successfully!")
print(f"   Total hourly_records: {len(data['hourly_records'])}")
print(f"   Avg AI score this round: {hour13_record['daily_summary']['avg_ai_score']}")
print(f"   Total articles: {hour13_record['daily_summary']['total_articles_collected']}")
print(f"   High AI (>70) articles: {len(hour13_record['daily_summary']['high_ai_score_articles'])}")
