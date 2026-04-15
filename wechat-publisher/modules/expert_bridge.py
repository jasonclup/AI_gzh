# -*- coding: utf-8 -*-
"""
专家桥接器 - 将飞书AI机器人连接到WorkBuddy领域专家知识库

方案B核心：
每个角色不再只是"不同说话风格"，而是背后接入了真正的领域专业知识。
通过RAG查询对应领域的知识库，让机器人的发言更有深度和权威性。

角色-专家映射：
  内容写手   → 写作/创作专家知识库
  配图师     → 设计/AI绘图专家知识库  
  审稿员     → 编辑/出版/审核专家知识库
  产品经理   → 产品管理专家知识库
  开发工程师 → 编程/架构专家知识库
  测试专员   → QA/测试专家知识库
  热点猎手   → 数据分析/趋势专家知识库
  主控调度   → 项目管理专家知识库（可选）
"""

import json
import time
import re
from pathlib import Path

# 角色→知识库映射
EXPERT_MAP = {
    "writer": {
        "name": "写作专家",
        "knowledge_bases": ["Typescript", "微信小程序"],  # 可替换为更匹配的KB
        "expertise": [
            "爆款标题写法（数字法、冲突法、悬念法、反差法）",
            "第一人称叙事技巧",
            "情绪曲线设计（好奇→共鸣→震撼→转发欲）",
            "金句提炼方法",
            "开头3秒法则",
            "公众号排版规范",
            "读者心理洞察",
        ],
        "default_advice": "从用户视角切入，用具体场景代替抽象概念，让读者有代入感"
    },
    "artist": {
        "name": "设计/AI绘图专家",
        "knowledge_bases": [],
        "expertise": [
            "构图法则（三分法、引导线、对称、框架式）",
            "色彩心理学（冷暖色调情绪影响）",
            "视觉层次（大小/对比/间距）",
            "AI绘图Prompt工程",
            "品牌一致性维护",
            "信息图表设计原则",
            "封面图CTR优化",
        ],
        "default_advice": "主视觉要3秒内抓住注意力，配色不超过3种主色，保持统一调性"
    },
    "reviewer": {
        "name": "编辑/审核专家",
        "knowledge_bases": [],
        "expertise": [
            "敏感词检测标准",
            "AI文本特征识别方法",
            "事实核查流程",
            "版权风险规避",
            "可读性评估体系（Flesch阅读难度等）",
            "标题党边界判断",
            "合规发布 checklist",
        ],
        "default_advice": "重点检查数据引用来源、极端表述、未经证实的信息"
    },
    "product_manager": {
        "name": "产品管理专家",
        "knowledge_bases": [],
        "expertise": [
            "用户画像构建方法",
            "A/B测试设计",
            "转化漏斗优化",
            "KPI指标体系设计",
            "竞品分析方法",
            "MVP思维",
            "数据驱动决策",
        ],
        "default_advice": "先定义成功指标再执行，用数据验证假设而非凭感觉"
    },
    "developer": {
        "name": "编程/架构专家",
        "knowledge_bases": ["Typescript"],
        "expertise": [
            "API性能优化策略",
            "缓存设计模式",
            "异步处理最佳实践",
            "错误重试机制",
            "日志与监控",
            "代码质量保障",
            "安全防护要点",
        ],
        "default_advice": "优先保证核心链路稳定，监控比优化更重要"
    },
    "tester": {
        "name": "QA测试专家",
        "knowledge_bases": [],
        "expertise": [
            "测试金字塔（单元/集成/E2E）",
            "边界值分析法",
            "等价类划分",
            "回归测试策略",
            "自动化测试框架",
            "性能测试方法",
            "Bug生命周期管理",
        ],
        "default_advice": "不仅要测正常流，更要测异常流——系统往往在边缘case翻车"
    },
    "hot_fetcher": {
        "name": "数据分析/趋势专家",
        "knowledge_bases": [],
        "expertise": [
            "热点追踪方法论",
            "多平台数据交叉验证",
            "话题生命周期判断",
            "热度预测模型",
            "竞品内容分析框架",
            "SEO关键词研究",
            "舆情监测技巧",
        ],
        "default_advice": "不要追已经爆了的话题，要追正在上升但还没到顶点的"
    },
    "coordinator": {
        "name": "项目管理专家",
        "knowledge_bases": [],
        "expertise": [
            "敏捷项目管理",
            "跨团队协作机制",
            "风险管理",
            "进度把控方法",
            "沟通效率提升",
            "复盘方法论",
            "OKR目标管理",
        ],
        "default_advice": "明确目标→分解任务→设定里程碑→跟踪进展→快速调整"
    }
}


class ExpertBridge:
    """
    专家桥接器 — 为每个角色注入领域专业知识
    
    使用方式：
        bridge = ExpertBridge()
        
        # 获取角色的专业建议
        advice = bridge.get_expert_advice("writer", "如何写出高点击率标题")
        
        # 获取角色的专业知识清单
        expertise = bridge.get_role_expertise("artist")
        
        # 用专业知识增强消息
        enhanced_msg = bridge.enrich_message("reviewer", original_msg, topic="GPT-5")
    """

    def __init__(self):
        self.expert_map = EXPERT_MAP
        self._cache = {}  # 简单缓存避免重复查询

    def get_role_config(self, role: str) -> dict:
        """获取指定角色的专家配置"""
        return self.expert_map.get(role, {
            "name": "通用专家",
            "knowledge_bases": [],
            "expertise": [],
            "default_advice": ""
        })

    def get_expert_advice(self, role: str, question: str) -> str:
        """
        基于角色专业知识回答问题
        
        在实际接入RAG时，这里会调用对应的知识库查询。
        目前使用本地专业知识库模拟。
        """
        config = self.get_role_config(role)
        expertise_list = config.get("expertise", [])
        
        # 根据问题关键词匹配合适的专业知识
        question_lower = question.lower()
        
        # 尝试找到最相关的知识点
        best_match = None
        best_score = 0
        
        for item in expertise_list:
            # 计算简单相关性
            score = sum(1 for kw in re.findall(r'[\u4e00-\u9fff]+', item) 
                       if kw in question_lower or question_lower in kw)
            if score > best_score:
                best_score = score
                best_match = item
        
        if best_match:
            return f"💡 **{config['name']}观点**：基于{best_match}，{config['default_advice']}"
        else:
            return f"💡 **{config['name']}建议**：{config['default_advice']}"

    def get_role_expertise(self, role: str) -> list[str]:
        """获取角色的全部专业知识领域"""
        config = self.get_role_config(role)
        return config.get("expertise", [])

    def enrich_message(self, role: str, base_message: str,
                       context: dict = None) -> str:
        """
        用专业知识增强原始消息
        
        Args:
            role: 角色标识
            base_message: 人格引擎生成的原始消息
            context: 额外上下文（话题、阶段等）
            
        Returns:
            增强后的消息（附加专家见解）
        """
        if not context:
            return base_message
            
        config = self.get_role_config(role)
        expertise = config.get("expertise", [])
        
        # 根据当前任务阶段选择一个相关的专业点
        topic = context.get("topic", "")
        stage = context.get("stage", "")
        
        # 选择一个跟当前场景相关的专业知识
        selected_expertise = None
        for exp in expertise:
            # 简单的关键词匹配
            if any(kw in topic + stage for kw in re.findall(r'[\u4e00-\u9fff]{2,}', exp)):
                selected_expertise = exp
                break
        
        # 如果没有匹配到，随机选一个
        import random as _rnd
        if not selected_expertise and expertise:
            selected_expertise = _rnd.choice(expertise)
        
        if selected_expertise:
            # 将专业知识自然地融入消息
            expert_tag = (
                f"\n\n📚 *{config['name']}补充*："
                f"{selected_expertise} — 这是我在这个领域的经验积累。"
            )
            return base_message + expert_tag
        
        return base_message

    def get_expert_checklist(self, role: str) -> str:
        """
        获取角色的专业检查清单
        用于审稿员、测试专员等需要结构化检查的角色
        """
        config = self.get_role_config(role)
        checklists = {
            "reviewer": [
                "☐ 数据来源是否可追溯？",
                "☐ 是否有夸大/绝对化表述？",
                "☐ 敏感词扫描是否通过？",
                "☐ AI痕迹评分是否在安全范围？",
                "☐ 引用的事实是否经过核查？",
                "☐ 是否存在潜在的侵权风险？",
                "☐ 段落逻辑是否通顺？",
                "☐ 结尾是否有行动号召？",
            ],
            "tester": [
                "☐ 主流程端到端是否通畅？",
                "☐ 空输入/超长输入是否正确处理？",
                "☐ API超时时是否有降级？",
                "☐ 飞书消息是否全部送达？",
                "☐ 图片生成是否有兜底？",
                "☐ AI服务不可用时能否优雅降级？",
                "☐ 日志是否完整可追溯？",
            ],
            "artist": [
                "☐ 封面图是否符合CTR优化标准？",
                "☐ 配色方案是否与文章情绪匹配？",
                "☐ 所有图片尺寸规格是否一致？",
                "☐ 视觉风格是否统一？",
                "☐ 图文比例是否合理？",
            ],
            "writer": [
                "☐ 标题是否有吸引力（数字/冲突/悬念）？",
                "☐ 前3秒是否能抓住注意力？",
                "☐ 段落长度是否适合手机阅读？",
                "☐ 是否有可被转发的金句？",
                "☐ 情绪曲线是否有起伏？",
                "☐ 第一人称视角是否自然？",
            ]
        }
        items = checklists.get(role, [])
        name = config.get("name", "专家")
        header = f"\n📋 {name} Checklist：\n"
        body = "\n".join(items) if items else "(无专用检查清单)"
        return header + body


# ---- 全局单例 ----
_bridge_instance = None

def get_expert_bridge() -> ExpertBridge:
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ExpertBridge()
    return _bridge_instance


# ---- 测试入口 ----
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    
    bridge = ExpertBridge()
    
    print("=" * 50)
    print("  Expert Bridge Test")
    print("=" * 50)
    print()
    
    # 展示每个角色连接到的专家
    for role, config in EXPERT_MAP.items():
        print(f"🔗 {role} → {config['name']}")
        print(f"   专业知识({len(config['expertise'])}项): {config['expertise'][:3]}...")
        advice = bridge.get_expert_advice(role, "如何提高内容质量")
        print(f"   建议: {advice[:60]}...")
        print()
    
    # 展示检查清单
    print("\n--- 审稿员 Checklist ---")
    print(bridge.get_expert_checklist("reviewer"))
    
    print("\n--- 测试专员 Checklist ---")
    print(bridge.get_expert_checklist("tester"))
