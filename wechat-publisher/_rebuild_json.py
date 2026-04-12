# -*- coding: utf-8 -*-
"""
完全重建 2026-04-11.json 文件
包含08:00 + 09:00 + 10:00 三条完整记录
"""
import json

JSON_FILE = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-11.json"

# 完整的3条记录数据 - 使用纯Python dict构建避免JSON字符串拼接问题
full_data = {
    "date": "2026-04-11",
    "hourly_records": [
        # ====== 08:00 记录（从原始数据重建daily_summary部分） ======
        {
            "hour": "08",
            "collected_at": "2026-04-11T08:17:00+08:00",
            "hot_topics": [
                {
                    "topic": "夫妻称用AI写公众号年赚200万被封号",
                    "heat_level": "极高",
                    "hot_value": 28505808,
                    "source": "今日头条热搜TOP1",
                    "competitor_articles": [
                        {"title": "搬起石头砸自己脚！AI写作年赚200万夫妻被封号！", "account": "知乎专栏/网易新闻", "publish_time": "2026-04-10T20:00:00+08:00", "estimated_reads": "8w+", "ai_score": 18, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["标题口语化有鲜明个人态度", "追踪了封号最新进展引用平台具体措辞", "分析了商业模式本质", "语言有评论员的讽刺幽默感"], "summary": "事件跟进评论 核心发现年入200万大部分来自学员保证金。", "url": "https://zhuanlan.zhihu.com/p/2025889647281054474"},
                        {"title": "AI写作年赚200万夫妻被封号 如何善用AI？", "account": "羊城晚报/YCWB", "publish_time": "2026-04-11T01:00:00+08:00", "estimated_reads": "5w+", "ai_score": 42, "ai_confidence": "medium", "ai_category": "suspected_ai_assisted", "ai_evidence": ["如何善用AI标准框架", "事件回顾与多家媒体雷同", "建议泛化缺乏实操案例"], "summary": "利用封号事件引出AI工具使用方法的观点文。", "url": "https://news.ycwb.com/ikimvkotjk/content_54056485.htm"},
                        {"title": "用AI写公众号年赚200万夫妻被封号 微信称反对完全由AI生成", "account": "IT之家", "publish_time": "2026-04-10T22:00:00+08:00", "estimated_reads": "6w+", "ai_score": 12, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["IT之家科技媒体原创报道", "独家揭示收入真实构成", "引用微信官方回应"], "summary": "IT之家深度调查 拆解年赚200万真实构成。", "url": "https://www.ithome.com/0/937/700.htm"}
                    ],
                    "analysis": {"title_patterns": "三派：讽刺型/借力型/事实型", "content_structure": "事件类从发生了什么转向意味着什么", "image_style": "平台公告截图/收入模式图表", "best_publish_window": "事件发酵48-72小时", "ai_article_ratio": "33%"}
                },
                {
                    "topic": "中国AI芯片格局反转 2026国产TOP10发布",
                    "heat_level": "高",
                    "hot_value": 778884,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "炸场！2026国产AI芯片TOP10重磅发布 中国芯格局彻底改写！", "account": "网易号/摩尔精英", "publish_time": "2026-03-31T15:00:00+08:00", "estimated_reads": "10w+", "ai_score": 68, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["情绪词堆砌 炸场/重磅/彻底改写", "TOP10榜单便于批量生产", "段落长度异常均匀"], "summary": "国产AI芯片TOP10榜单文章 典型AI生成爆款。", "url": "https://www.163.com/dy/article/KPH89SR405566SXC.html"},
                        {"title": "拆解六家国产AI芯片财报 蚕食英伟达市场 押注哪些方向？", "account": "腾讯新闻/N视频", "publish_time": "2026-04-09T14:00:00+08:00", "estimated_reads": "12w+", "ai_score": 15, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["南都N视频记者原创报道", "覆盖六家2025财报一手财务数据", "语言专业体现记者理解力"], "summary": "六家国产AI芯片企业财报深度拆解 高质量行业财经报道。", "url": "https://news.qq.com/rain/a/20260409A076YR00"},
                        {"title": "2026年国产AI芯片深度研判 资本突围生态重塑与后英伟达时代", "account": "Axo开放智库", "publish_time": "2026-01-30T10:00:00+08:00", "estimated_reads": "3w+", "ai_score": 72, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["大词堆砌 资本突围/生态重塑", "结构极度标准化", "模糊预测充斥全文"], "summary": "典型AI生成行业研判报告 方向正确但无独家洞察。", "url": "https://openaxo.com/innovation/china-domestic-ai-chip-2026"}
                    ],
                    "analysis": {"title_patterns": "榜单式标题成AI生成爆款新宠", "content_structure": "财报解读人写vs榜单盘点AI vs行业研判AI", "best_publish_window": "财报季3-4月/8-9月", "ai_article_ratio": "67%"}
                },
                {
                    "topic": "外交部回应日本降级日中关系",
                    "heat_level": "极高",
                    "hot_value": 38478816,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "外交部回应日本降级日中关系 日方应以实际行动维护政治基础", "account": "腾讯新闻", "publish_time": "2026-04-10T16:00:00+08:00", "estimated_reads": "30w+", "ai_score": 5, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["权威媒体官方回应报道", "完整引用发言人原话"], "summary": "外交部关于日本蓝皮书降级表述的官方报道。", "url": "https://news.qq.com/rain/a/20260410A05O6E00"},
                        {"title": "日本降级日中关系的深层信号 高市早苗对华强硬路还能走多远？", "account": "网易号/国际时评", "publish_time": "2026-04-11T07:00:00+08:00", "estimated_reads": "8w+", "ai_score": 65, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["问号制造悬念+关联人物", "结构模板化", "预测模棱两可无学者访谈"], "summary": "利用外交热点制作的国际局势分析 AI模板文。", "url": "https://www.163.com/dy/article/KQ76C2AC05568W0A.html"},
                        {"title": "日本降级日中关系背后 一份蓝皮书折射出的东亚格局变迁", "account": "环球网/每经网", "publish_time": "2026-04-10T18:00:00+08:00", "estimated_reads": "15w+", "ai_score": 28, "ai_confidence": "medium", "ai_category": "suspected_ai_assisted", "ai_evidence": ["折射出句式", "有历史对比但深度有限"], "summary": "以外交蓝皮书措辞变化切入分析中日关系走向 中等质量。", "url": "https://www.nbd.com.cn/articles/2026-04-10/4334068.html"}
                    ],
                    "analysis": {"title_patterns": "事实陈述型/深度分析型(问号)/历史脉络型(折射出)", "content_structure": "通报事实到补充背景到延伸分析 第三段易AI化", "ai_article_ratio": "33%"}
                },
                {
                    "topic": "金正恩与王毅紧紧握手后拥抱",
                    "heat_level": "极高",
                    "hot_value": 34817073,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "加强协调配合反对霸权主义——中朝外长在京举行会谈", "account": "环球网", "publish_time": "2025-09-29T10:00:00+08:00", "estimated_reads": "20w+", "ai_score": 5, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["权威外交新闻报道", "完整官方表述"], "summary": "环球网中朝外长会谈官方通报 最权威信息源头。", "url": "https://hqtime.huanqiu.com/share/article/4OVwIJSZeWE"},
                        {"title": "王毅谈中朝友谊 焕发勃勃生机两国关系展开新篇章", "account": "环球网两会频道", "publish_time": "2026-03-27T16:00:00+08:00", "estimated_reads": "10w+", "ai_score": 35, "ai_confidence": "medium", "ai_category": "suspected_ai_assisted", "ai_evidence": ["标准报道格式 以官方表态为主", "创新性不足偏通稿性质"], "summary": "王毅关于中朝关系的答记者问 信息准确但分析有限。", "url": "https://lianghui.huanqiu.com/article/9CaKrnKiP6B"},
                        {"title": "金正恩王毅握手拥抱背后的深意 蜜月期？还是战术性靠近？", "account": "国际观察类账号", "publish_time": "2026-04-11T08:00:00+08:00", "estimated_reads": "12w+", "ai_score": 75, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["二元对立设问标题", "A/B设问+折中结论安全公式", "缺乏真正专家访谈"], "summary": "AI擅长的二元对立框架地缘政治分析。", "url": ""}
                    ],
                    "analysis": {"title_patterns": "标准通报式/意义解读式(AI占比高)", "content_structure": "AI外交解读模板 描述场面到列举案例到AB分析到折中结论", "ai_article_ratio": "33%"}
                },
                {
                    "topic": "徐某发表侮辱运动员言论被拘 全红婵网暴案",
                    "heat_level": "极高",
                    "hot_value": 25793122,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "广州警方通报全红婵遭网暴事件 徐某微信群内发表侮辱性言论", "account": "澎湃新闻", "publish_time": "2026-04-10T19:30:00+08:00", "estimated_reads": "40w+", "ai_score": 5, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["警方通报绝对一手信源", "完整违法事实认定和处罚结果"], "summary": "广州警方全红婵网暴案官方通报 最权威信息源头。", "url": "https://www.thepaper.cn/newsDetail_forward_32943374"},
                        {"title": "网暴全红婵的被拘10天罚款 网友却都说罚轻了", "account": "搜狐社会", "publish_time": "2026-04-11T06:00:00+08:00", "estimated_reads": "15w+", "ai_score": 25, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["标题呈现舆论倾向罚轻了", "披露群公告惊人细节", "语言有正义感色彩"], "summary": "聚焦处罚争议 披露群公告细节引发讨论。", "url": "https://www.sohu.com/a/1007902741_122590197"},
                        {"title": "从全红婵被网暴看体育饭圈化的危害与治理困境", "account": "体育评论自媒体", "publish_time": "2026-04-10T23:00:00+08:00", "estimated_reads": "10w+", "ai_score": 70, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["宏大叙事标题AI学术包装", "问题分析四段式模板", "建议泛泛无可操作性"], "summary": "AI生成的体育饭圈化分析文 模板化严重。", "url": ""}
                    ],
                    "analysis": {"title_patterns": "事实通报/舆论焦点/宏大议题(几乎都是AI)", "content_structure": "通报到跟进到反思 反思环节最易AI化", "ai_article_ratio": "33%"}
                },
                {
                    "topic": "美伊停火谈判今日举行",
                    "heat_level": "极高",
                    "hot_value": 23338582,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "美伊同意停火并将于4月10日开启谈判 伊朗公布十点计划", "account": "腾讯新闻", "publish_time": "2026-04-08T14:00:00+08:00", "estimated_reads": "25w+", "ai_score": 8, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["权威突发新闻", "含伊朗国安委员会声明核心内容", "准确记录时间线"], "summary": "美伊停火突发报道 最及时准确信息汇总。", "url": "https://news.qq.com/rain/a/20260408A03CGF00"},
                        {"title": "谈判在即巴基斯坦举国严阵以待 30人先遣队已到", "account": "搜狐国际", "publish_time": "2026-04-10T18:00:00+08:00", "estimated_reads": "12w+", "ai_score": 32, "ai_confidence": "medium", "ai_category": "suspected_ai_assisted", "ai_evidence": ["标题有画面感", "以东道主筹备安保为主线 有具体细节"], "summary": "从东道主巴基斯坦视角切入谈判前瞻 有现场感。", "url": "https://www.sohu.com/a/1007679394_121984036"},
                        {"title": "美伊世纪谈判即将开启 五大悬念牵动全球能源格局与中东未来", "account": "国际时政分析号", "publish_time": "2026-04-11T07:00:00+08:00", "estimated_reads": "8w+", "ai_score": 78, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["四吸睛要素叠加 世纪谈判/五大悬念/全球能源格局", "列表式结构AI最高效生产格式", "安全句式一方面另一方面不敢下注"], "summary": "典型AI生成时政分析爆文 五大悬念框架最高效生产模式 本轮最高评分。", "url": ""}
                    ],
                    "analysis": {"title_patterns": "事实通报→筹备情况→悬念分析(AI浓度递增)", "content_structure": "X大悬念/看点/关键列表式是AI时政文最爱", "ai_article_ratio": "33%", "ai_viral_features": ["X大悬念列表式标题是AI时政文最强识别特征"]}
                },
                {
                    "topic": "专家谈1吨旧手机能提炼200克黄金",
                    "heat_level": "中高",
                    "hot_value": 472417,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "1吨旧手机能提炼200克黄金？专家澄清真相", "account": "网易新闻/上观新闻", "publish_time": "2026-04-11T08:00:00+08:00", "estimated_reads": "15w+", "ai_score": 10, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["记者实地调查走访多位专家", "厘清关键事实差异 功能机可达200g智能机远低于此", "信息密度极高每段有增量"], "summary": "上观新闻联合辟谣调查 厘清适用条件 多位业内权威解读。", "url": "https://c.m.163.com/news/a/KQ78IRNB0514D3UH.html"},
                        {"title": "1吨旧手机能提炼200克黄金 专家回应 智能机含金量显著降低", "account": "腾讯新闻", "publish_time": "2026-04-11T09:00:00+08:00", "estimated_reads": "10w+", "ai_score": 20, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["专家辟谣快讯", "简洁呈现核心辟谣信息", "引用权威表述"], "summary": "专家辟谣快讯 简洁准确传达核心。", "url": "https://new.qq.com/rain/a/20260411A00IEQ00"},
                        {"title": "旧手机炼金热潮背后 电子垃圾回收的真相机遇与骗局", "account": "科普/财经类账号", "publish_time": "2026-04-11T10:00:00+08:00", "estimated_reads": "6w+", "ai_score": 62, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["三段式宏大叙事 真相机遇与骗局", "全景扫描模式 信息量大实为公开资料重组", "模糊信源必然出现"], "summary": "借热门话题切入电子垃圾回收科普 AI擅长借热点加全景扫描模式。", "url": "https://news.online.sh.cn/news/gb/content/2026-04/11/content_10441219.htm"}
                    ],
                    "analysis": {"title_patterns": "直击型(人写) / 快讯型(人写) / 借力型(AI最高)", "ai_article_ratio": "33%"}
                },
                {
                    "topic": "A股交易规则重大调整 ST股5%改10%+盘后交易全覆盖",
                    "heat_level": "高",
                    "hot_value": 11589596,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "重磅！A股双规齐发重塑市场交易生态", "account": "CA Markets/财经号", "publish_time": "2026-04-07T14:00:00+08:00", "estimated_reads": "8w+", "ai_score": 76, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["双规齐发/重塑生态AI大词组合", "里程碑意义开场白", "完美AI模板 政策概述到条文解读到市场影响", "万能好评词堆砌 引用北大教授背书"], "summary": "A股新规综合分析 典型AI金融政策解读文 看起来专业无实战价值。", "url": ""},
                        {"title": "交易规则重大调整！A股风险警示股告别5%涨跌幅 涉超130股", "account": "同花顺/北京商报", "publish_time": "2026-04-10T18:00:00+08:00", "estimated_reads": "20w+", "ai_score": 8, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["同花顺/北京商报权威信源", "核心信息精确 ST股5%调至10%涉及132只个股", "简洁明了投资者可操作"], "summary": "沪深交易所交易规则修订征求意见快讯 核心信息精确简洁实用。", "url": "http://stock.10jqka.com.cn/20260410/c675909062.shtml"},
                        {"title": "A股交易迎新规！盘后固定价格交易全覆盖 主板ST股涨跌幅提至10%", "account": "今日头条财经", "publish_time": "2026-04-10T20:00:00+08:00", "estimated_reads": "15w+", "ai_score": 38, "ai_confidence": "medium", "ai_category": "suspected_ai_assisted", "ai_evidence": ["标题概括两大核心变化", "基于交易所官方文件解读 信息准确但分析有限"], "summary": "三大调整要点综合解读 合格财经资讯。", "url": "https://www.toutiao.com/article/7627140799674843658/"}
                    ],
                    "analysis": {"title_patterns": "精准信息型(人写) / 宏观叙事型(AI重灾区) / 综合解读型(人机混合)", "ai_article_ratio": "33%", "ai_viral_features": ["AI金融文新伪装术 引用真实学者姓名加编造观点"]}
                },
                {
                    "topic": "几毛钱一片药被老外捧成神药 黄连素海外爆火",
                    "heat_level": "中高",
                    "hot_value": 21117622,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "几毛钱一片的药被老外捧成减肥神药 黄连素海外走红调查", "account": "腾讯新闻/新快报", "publish_time": "2026-04-10T18:00:00+08:00", "estimated_reads": "20w+", "ai_score": 12, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["新快报记者原创调查", "价格反差呈现 几毛钱vs高端补充剂", "医生权威澄清 语言生动"], "summary": "黄连素海外爆火现象调查 价格反差加医学澄清 人写标杆。", "url": "https://news.qq.com/rain/a/20260410A07S5B00"},
                        {"title": "几毛钱一片药被老外捧成神药 专家不建议自行服用", "account": "同花顺/39健康网", "publish_time": "2026-04-11T08:00:00+08:00", "estimated_reads": "12w+", "ai_score": 15, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["医疗健康新闻 专家明确不建议", "指出炒作风险 简洁实用"], "summary": "医学界专家回应 不建议自行服用减肥。", "url": "https://t.10jqka.com.cn/pid_611927155.shtml"},
                        {"title": "中国几毛钱一片药被外国人捧成神药反映的文化心理和国际趋势", "account": "知乎问答/文化观察", "publish_time": "2026-04-10T22:00:00+08:00", "estimated_reads": "10w+", "ai_score": 72, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["从小现象强行升到文化心理高度", "这反映了AI标志性升华句", "每个角度都说正确废话无一深入"], "summary": "将消费现象强行上升到理论高度的AI文化分析。", "url": "https://www.zhihu.com/question/2025952155119404840"}
                    ],
                    "analysis": {"title_patterns": "反差型(人写爆款) / 警示型(实用) / 升级型(小题大做AI)", "ai_article_ratio": "33%"}
                },
                {
                    "topic": "菲律宾为何急推南海油气合作",
                    "heat_level": "中高",
                    "hot_value": 17289646,
                    "source": "今日头条热搜",
                    "competitor_articles": [
                        {"title": "陈利君：菲律宾为何急推南海油气合作", "account": "环球网/环球时报", "publish_time": "2026-04-11T08:30:00+08:00", "estimated_reads": "10w+", "ai_score": 8, "ai_confidence": "high", "ai_category": "human_written", "ai_evidence": ["署名专家原创分析", "从菲国内能源紧急状态切入", "论点明确体现学者独立判断"], "summary": "自然资源专家陈利君深度分析 高质量专家学者评论。", "url": "https://opinion.huanqiu.com/article/4R6y9mMkj3d"},
                        {"title": "菲律宾能源紧急！马科斯急求中国合作 南海油气谈判重启背后", "account": "搜狐国际", "publish_time": "2026-04-05T14:00:00+08:00", "estimated_reads": "12w+", "ai_score": 35, "ai_confidence": "medium", "ai_category": "suspected_ai_assisted", "ai_evidence": ["标题有紧迫感 编辑水平在线", "多维度信息整合 但深度一般"], "summary": "从菲能源危机角度切入 分析 信息覆盖面广深度一般。", "url": "https://www.sohu.com/a/1005937390_122380408"},
                        {"title": "南海博弈新变局：菲律宾油气困局与中国战略抉择", "account": "地缘政治分析号", "publish_time": "2026-04-11T09:00:00+08:00", "estimated_reads": "6w+", "ai_score": 74, "ai_confidence": "high", "ai_category": "likely_ai_generated", "ai_evidence": ["AI味浓 新变局/困局/战略抉择三连大词", "博弈棋局牌面隐喻滥用", "两面平衡结论必然出现"], "summary": "AI地缘政治分析代表样本 博弈困局抉择经典叙事。", "url": ""}
                    ],
                    "analysis": {"title_patterns": "专家署名型(人写) / 紧迫叙事型(人机混合) / 博弈分析型(AI重灾区)", "ai_article_ratio": "33%"}
                }
            ],
            "daily_summary": {
                "total_topics_analyzed": 10,
                "total_articles_collected": 30,
                "avg_ai_score": 41,
                "high_ai_ratio_topics": ["中国AI芯片格局反转(67%)", "美伊停火谈判(33% 含最高分78分)", "菲律宾南海油气(33% 含74分)", "A股交易规则调整(33% 含76分)", "旧手机提炼黄金(33% 含62分)", "黄连素海外走红(33% 含72分)"],
                "key_findings": ["最高AI评分78分 五大悬念列表式确认为AI时政文最强识别特征", "新变种 二元对立设问标题模式 AI制造深度错觉", "AI金融文新招 名人背书法 引用真学者加泛泛观点", "小题大做模式确认 将有趣现象强行上升到理论高度", "人写标杆 上观新闻旧手机炼金调查 信息密度极高", "人写标杆 南都六家芯片财报拆解 硬核行业分析", "平均AI评分41分 较稳定", "事件类规律 社会突发事件33% 科技行业67%"],
                "high_ai_score_articles": [
                    {"title": "美伊世纪谈判五大悬念牵动全球能源格局", "ai_score": 78, "reason": "X大悬念列表式AI时政文标杆"},
                    {"title": "重磅A股双规齐发重塑市场交易生态", "ai_score": 76, "reason": "AI金融政策文 三词联用加教授背书"},
                    {"title": "炸场2026国产AI芯片TOP10重磅发布", "ai_score": 68, "reason": "AI榜单类 情绪词堆砌均匀段落"},
                    {"title": "菲律宾油气困局与中国战略抉择", "ai_score": 74, "reason": "AI地缘政治文 三连大词"},
                    {"title": "中国几毛钱药文化心理国际趋势", "ai_score": 72, "reason": "小题大做AI文化分析"},
                    {"title": "2026国产AI芯片深度研判资本突围", "ai_score": 72, "reason": "AI行业研判 大词加模糊预测"}
                ]
            }
        }
    ]
}

# 验证可以序列化
test_json = json.dumps(full_data, ensure_ascii=False)
print(f"08:00 record JSON OK! Length: {len(test_json)}")

# 写入文件
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(full_data, f, ensure_ascii=False, indent=2)

print(f"Written 08:00 record to {JSON_FILE}")
print("Now need to append 09:00 and 10:00 records")
