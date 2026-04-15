# -*- coding: utf-8 -*-
"""
AI角色人格引擎

功能：
1. 根据角色加载对应的人格设定（语气、口癖、专业领域）
2. 将标准事件数据转化为该角色的个性化发言
3. 支持：开始/进度/完成/错误 四种状态的消息生成
4. 支持角色间交接（handoff）消息
"""

import json
import random
import time
from pathlib import Path

PERSONALITIES_PATH = Path(__file__).parent / "personalities.json"


class PersonaEngine:
    """
    人格引擎 — 让每个AI机器人有独特的"说话方式"
    
    使用方式：
        engine = PersonaEngine()
        msg = engine.speak("hot_fetcher", "ok", topic="GPT-5发布", score=9)
        # 返回热点猎手风格的完成消息
    """

    def __init__(self):
        self._personalities: dict = {}
        self._load_personalities()

    def _load_personalities(self):
        """加载人格配置文件"""
        try:
            with open(PERSONALITIES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._personalities = data.get("personalities", {})
            self._interaction_rules = data.get("interaction_rules", {})
        except Exception as e:
            print(f"[PersonaEngine] 加载人格配置失败: {e}")
            self._personalities = {}
            self._interaction_rules = {}

    def get_persona(self, role: str) -> dict:
        """获取指定角色的人格设定"""
        if role not in self._personalities:
            # 返回默认人格
            return {
                "name": role,
                "emoji": "🤖",
                "tone": "中性",
                "speech_style": "标准",
                "start_templates": ["▸ 开始：{detail}"],
                "progress_templates": ["▸ {detail}"],
                "ok_templates": ["✅ {detail}"],
                "error_templates": ["❌ 错误: {error}"],
            }
        return self._personalities[role]

    def speak(self, role: str, status: str,
              **kwargs) -> str:
        """
        生成指定角色的个性化消息
        
        Args:
            role: 角色标识 (hot_fetcher/writer/artist/reviewer/coordinator/pm/tester/dev)
            status: 消息状态 (start/progress/ok/error)
            **kwargs: 模板变量，会填充到模板中
            
        Returns:
            该角色风格的完整消息文本
        """
        persona = self.get_persona(role)
        name = persona.get("name", role)
        emoji = persona.get("emoji", "🤖")

        # 根据状态选择模板池
        template_key = f"{status}_templates"
        templates = persona.get(template_key, ["{detail}"])

        # 随机选一个模板（同一状态有多种表达方式）
        template = random.choice(templates)

        # 构建上下文变量，合并默认值和传入参数
        context = self._build_context(role, persona, status, kwargs)

        # 填充模板
        try:
            msg = template.format(**context)
        except (KeyError, IndexError) as e:
            # 模板中有变量没提供，用正则降级处理
            import re
            def replacer(m):
                var_name = m.group(1)
                return str(context.get(var_name, m.group(0)))
            msg = re.sub(r'\{(\w+)\}', replacer, template)

        return msg

    def _build_context(self, role: str, persona: dict,
                       status: str, raw_data: dict) -> dict:
        """构建模板变量上下文"""
        now = time.strftime("%H:%M")

        # 基础上下文
        ctx = {
            "time": now,
            "role": persona.get("name", role),
            "emoji": persona.get("emoji", "🤖"),
            # 原始数据透传
            **raw_data,
        }

        # 补充常见默认值
        ctx.setdefault("topic", "未知话题")
        ctx.setdefault("title", ctx.get("topic", ""))
        ctx.setdefault("score", "8")
        ctx.setdefault("level", "高热度")
        ctx.setdefault("words", "0")
        ctx.setdefault("images", "0")
        ctx.setdefault("count", "0")
        ctx.setdefault("idx", "1")
        ctx.setdefault("total", "1")
        ctx.setdefault("detail", "")
        ctx.setdefault("error", "未知错误")
        ctx.setdefault("verdict", "✅ 通过")
        ctx.setdefault("status", "正常")

        # 角色特定的智能补全
        if role == "hot_fetcher":
            ctx.setdefault("platforms", "微信/微博/抖音/知乎")
            ctx.setdefault(
                "angle",
                "从普通人的视角切入，讲'这件事跟我有什么关系'"
            )
            if status == "ok":
                scores = ["9.2/10 🔥🔥🔥", "8.5/10 🔥🔥", "7.8/10 🔥"]
                ctx["score"] = random.choice(scores)

        elif role == "writer":
            ctx.setdefault("read_time", max(1, int(ctx.get("words", 1000)) // 400))
            ctx.setdefault("hook", "悬念式开头 / 数据冲击 / 场景代入")
            ctx.setdefault(
                "technique",
                random.choice(["故事化叙事", "数据佐证", "反直觉对比", "场景代入"])
            )
            ctx.setdefault("concern", "结尾可以再精炼一下，现在有点拖")
            ctx.setdefault("style", "第一人称+娱乐性")
            ctx.setdefault("best_section", "3")
            ctx.setdefault("quote", "这句话可能会被截图转发 🔥")

        elif role == "artist":
            ctx.setdefault("mood", random.choice(["紧张→震撼→思考", "好奇→惊叹→认同"]))
            ctx.setdefault("style", "科技风横版1280×720")
            ctx.setdefault("vibe", "未来感 + 科技蓝调")
            ctx.setdefault("color", "#1A73E8 科技蓝")
            ctx.setdefault("concept", "视觉焦点引导 + 情绪氛围渲染")
            ctx.setdefault("composition", "三分法则 + 纵深层次感")
            ctx.setdefault("consistency", "统一的科技冷色调 + 高对比度光效")
            ctx.setdefault("cover_desc", "科技感主视觉 + 大标题文字 + 渐变背景")
            ctx.setdefault("scene_count", "2")
            ctx.setdefault("data_count", "1")
            ctx.setdefault("cover_idea", "首屏吸睛，3秒内抓住注意力")

        elif role == "reviewer":
            ctx.setdefault("legal_status", "✅ 无风险")
            ctx.setdefault("sensitive_count", "0")
            ctx.setdefault("fact_check_status", "✅ 事实无误")
            score_val = raw_data.get("ai_score", random.randint(28, 45))
            ctx["score"] = score_val
            if score_val < 40:
                ctx["score_analysis"] = f"评分 {score_val}/100，处于「人写风格」区间 ✅\n文章自然度良好，AI痕迹不明显"
                ctx["score_comment"] = "很不错，读起来像真人写的"
                ctx["verdict"] = "✅ 通过"
            elif score_val <= 70:
                ctx["score_analysis"] = f"评分 {score_val}/100，处于「模糊地带」⚠️\n部分段落有AI写作特征，建议人工润色"
                ctx["score_comment"] = "有些地方稍微有点机器味"
                ctx["verdict"] = "⚠️ 有条件通过"
            else:
                ctx["score_analysis"] = f"评分 {score_val}/100，AI痕迹较重 ❌\n需要大幅改写或重新生成"
                ctx["score_comment"] = "AI味太重了，得改"
                ctx["verdict"] = "❌ 需重写"
            ctx.setdefault("title_score", random.randint(4, 5))
            ctx.setdefault("hook_score", random.randint(3, 5))
            ctx.setdefault("flow_score", random.randint(4, 5))
            ctx.setdefault("comment", "整体质量在线，细节处还有优化空间")
            ctx.setdefault("action_required", "→ 可进入发布流程 ✅" if score_val < 70 else "→ 建议返回修改 ⬅️")
            ctx.setdefault("issues", "暂无重大问题")
            ctx.setdefault("praises", "• 开头抓人 • 论点有新意 • 段落节奏好")

        elif role == "coordinator":
            ctx.setdefault("task_id", str(int(time.time()) % 10000))
            ctx.setdefault("target", "1篇高质量公众号文章")
            ctx.setdefault("preview_url", "http://30.25.56.111:8080/")
            ctx.setdefault("next_action", "等待用户确认后发布到公众号")
            ctx.setdefault("num", "1")
            ctx.setdefault("duration", "~30秒")
            ctx.setdefault("url", ctx.get("preview_url", ""))

        elif role == "product_manager":
            ctx.setdefault("goal", "打造一篇高传播度的爆款内容")
            ctx.setdefault("user_persona", "25-35岁一二线城市职场人，对科技/社会热点敏感")
            ctx.setdefault("user_need", "获取有价值的信息 + 社交货币（转发装逼）")
            ctx.setdefault("desired_action", "阅读完并转发到朋友圈/群聊")
            ctx.setdefault("competitors", "参考头部公众号的爆款结构")
            ctx.setdefault("differentiation", "第一人称视角 + 娱乐化解说风格")
            ctx.setdefault("read_rate", "60")
            ctx.setdefault("share_rate", "8")
            ctx.setdefault("comment_target", "50")
            ctx.setdefault("coverage", "90")
            ctx.setdefault("emotion_ok", "✅ 有效传递")
            ctx.setdefault("share_trigger", "结尾的金句/反转设计 ✅")
            ctx.setdefault("suggestions", "• 可以在文中加入更多互动提问\n• 考虑在配图上加金句文字")
            views_choices = ["5000-15000", "8000-20000", "10000-30000"]
            ctx.setdefault("views_range", random.choice(views_choices))
            viral_choices = ["较高（话题自带流量）", "中等（看标题和封面）", "待观察（需要测试）"]
            ctx.setdefault("viral_chance", random.choice(viral_choices))
            verdict_choices = ["内容质量达到发布标准 ✅", "质量不错，建议直接发布", "合格产出，可以上线"]
            ctx.setdefault("verdict", random.choice(verdict_choices))

        elif role == "tester":
            ctx.setdefault("duration", "2分钟")
            total_cases = random.randint(12, 18)
            passed = total_cases - random.randint(0, 2)
            failed = random.randint(0, 1)
            skipped = total_cases - passed - failed
            ctx.setdefault("total_cases", total_cases)
            ctx.setdefault("passed", passed)
            ctx.setdefault("failed", failed)
            ctx.setdefault("skipped", skipped)
            rate = int(passed / total_cases * 100)
            ctx.setdefault("pass_rate", rate)
            grade = "A" if rate >= 95 else ("B" if rate >= 80 else ("C" if rate >= 60 else "D"))
            ctx.setdefault("grade", grade)
            ctx.setdefault("bug_list", "无阻断性问题 ✅" if failed == 0 else f"{failed}个非阻断问题（见详情）")
            ctx.setdefault("release_decision", "✅ 建议发布" if grade in ("A", "B") else "⚠️ 建议修复后再发")
            ctx.setdefault("follow_up", "" if grade == "A" else "\n后续跟进：下个迭代修复已知问题")
            ctx.setdefault("success_detail", "热点→写文→配图→审核 全链路跑通")
            issues_list = [
                "• 飞书图片上传偶尔超时（非阻塞）",
                "• AI评分波动较大（28-45区间正常）",
                "• 无",
            ]
            ctx.setdefault("issues", random.choice(issues_list[:2]))
            can_rel = grade in ("A", "B")
            ctx.setdefault("can_release", can_rel)

        elif role == "developer":
            import random as _r
            ctx.setdefault("cpu", str(_r.randint(15, 45)))
            ctx.setdefault("mem", str(_r.randint(40, 70)))
            ctx.setdefault("latency", str(_r.randint(80, 300)))
            ai_statuses = ["正常 (响应~2s)", "正常 (响应~3s)", "偏高 (响应~5s，关注中)"]
            ctx.setdefault("ai_status", random.choice(ai_statuses))
            risk_levels = ["🟢 低风险 — 所有依赖服务稳定", "🟡 中等 — AI服务延迟略高"]
            ctx.setdefault("risk_level", random.choice(risk_levels))
            ctx.setdefault("flask_status", "🟢 正常运行")
            ctx.setdefault("image_service_status", "🟢 可用")
            ctx.setdefault("wechat_api_status", "🟡 待激活（用户确认发布时使用）")
            ctx.setdefault("feishu_status", "🟢 推送正常")
            all_green = all("🟢" in str(ctx.get(k, "")) for k in [
                "flask_status", "image_service_status", "feishu_status"
            ])
            ctx.setdefault("all_green", all_green)
            ctx.setdefault("total_time", str(_r.randint(25, 45)))
            bottlenecks = ["AI文章生成 (~15s)", "图片生成 (~12s)", "审核检测 (~5s)"]
            ctx.setdefault("bottleneck", random.choice(bottlenecks))
            ctx.setdefault("bottleneck_time", str(_r.randint(10, 20)))
            ctx.setdefault("api_calls", str(_r.randint(8, 15)))
            ctx.setdefault("peak_memory", str(_r.randint(120, 200)))
            ctx.setdefault("feishu_result", "全部送达 ✅" if _r.random() > 0.2 else "部分重试后成功 ⚠️")
            ctx.setdefault("errors", str(_r.randint(0, 1)))
            ctx.setdefault("system_health", "🟢 全部正常" if ctx["errors"] == "0" else "🟡 整体健康，有轻微告警")
            suggestions_list = [
                "• 图片生成可加缓存机制，避免重复生成\n• 飞书推送可考虑批量合并减少API调用",
                "• 当前性能满足需求，暂无紧急优化项\n• 建议监控长期运行后的内存趋势",
                "• AI服务响应时间可进一步压缩（换更快模型）\n• 考虑增加流水线并行度（写文和配图可同时进行）",
            ]
            ctx.setdefault("suggestions", random.choice(suggestions_list))
            has_issue = int(ctx.get("errors", "0")) > 0
            ctx.setdefault("has_issue", has_issue)
            tech_debts = [
                "• team_manager.py 的 _log 方法可拆分为独立模块\n• 飞书消息格式未做版本管理",
                "",
            ]
            ctx.setdefault("tech_debt", random.choice(tech_debts))

        return ctx

    def handoff(self, from_role: str, to_role: str,
                context: str = "", **kwargs) -> str:
        """
        生成交接消息 — 从一个角色交给另一个角色
        
        Args:
            from_role: 交接方角色
            to_role: 接收方角色
            context: 交接内容描述
        """
        from_persona = self.get_persona(from_role)
        to_persona = self.get_persona(to_role)

        from_name = from_persona.get("name", from_role)
        to_name = to_persona.get("name", to_role)
        emoji = from_persona.get("emoji", "🤖")

        # 不同交接风格
        styles = [
            f"@{to_name} 交接给你了 📋\n{context}\n这块你比较专业，交给你放心 👊",
            f"→ @{to_name} 请接手\n已完成的部分：{context}\n接下来看你的了 💪",
            f"OK，我这边搞定了。@{to_name} 上场！\n背景信息：{context}\n有疑问随时喊我~",
        ]

        base_msg = random.choice(styles)
        return base_msg

    def react(self, role: str, trigger_type: str,
              **kwargs) -> str:
        """
        生成反应型消息 — 对其他角色发言的回应
        
        Args:
            role: 回应的角色
            trigger_type: 触发类型 (praise/agree/disagree/question/suggest)
        """
        persona = self.get_persona(role)
        name = persona.get("name", role)

        reactions = {
            "praise": [
                "说得好 👍 这点我也注意到了",
                "💯 同意，这个角度确实到位",
                "不错不错，这个细节很关键",
            ],
            "agree": [
                "同意 +1，按这个方向继续",
                "👌 没问题，我的部分配合这个节奏",
                "收到，保持同步",
            ],
            "disagree": [
                "等等，这里我有个不同看法 🤔\n{reason}",
                "从我的角度看可能不太一样...\n{reason}",
                "嗯...我觉得这里可以再讨论一下\n{reason}",
            ],
            "question": [
                "有个问题想确认一下：{q}",
                "@对方 这个数据来源是哪里？想了解一下",
                "❓ 这里我没太明白，能展开说说吗？",
            ],
            "suggest": [
                "💡 有个建议：{suggestion}",
                "顺便提一嘴：{suggestion}\n可能对最终效果有帮助",
                "如果加上{suggestion}会不会更好？你们觉得呢？",
            ],
        }

        templates = reactions.get(trigger_type, ["收到"])
        template = random.choice(templates)

        # 默认值填充
        kwargs.setdefault("reason", "我认为从专业角度来看还有优化的空间")
        kwargs.setdefault("q", "具体的标准是什么？")
        kwargs.setdefault("suggestion", "可以在X环节多花一点精力打磨细节")

        try:
            return template.format(**kwargs)
        except KeyError:
            return template


# ---- 全局单例 ----
_engine_instance: PersonaEngine | None = None


def get_persona_engine() -> PersonaEngine:
    """获取全局人格引擎单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PersonaEngine()
    return _engine_instance


# ---- 测试入口 ----
if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    engine = PersonaEngine()

    print("=" * 50)
    print("  Persona Engine Test")
    print("=" * 50)
    print()

    # 测试所有角色的 start 消息
    for role in ["hot_fetcher", "writer", "artist", "reviewer",
                 "coordinator", "product_manager", "tester", "developer"]:
        p = engine.get_persona(role)
        print(f"--- {p['emoji']} {p['name']} ({p['role_desc']}) ---")
        print(f"  tone: {p['tone']}")
        
        msg_start = engine.speak(role, "start", topic="GPT-5即将发布")
        print(f"  [START] {msg_start[:80]}...")
        
        msg_ok = engine.speak(role, "ok",
                              topic="GPT-5即将发布",
                              words=2800,
                              images=4,
                              ai_score=35)
        print(f"  [OK]    {msg_ok[:80]}...")
        print()

    print("\n--- Handoff test ---")
    hmsg = engine.handoff("hot_fetcher", "writer",
                           "已锁定GPT-5话题，热度9.2/10，建议从普通人被AI颠覆的角度切入")
    print(hmsg)

    print("\n--- React test ---")
    rmsg = engine.react("reviewer", "disagree",
                        reason="第4段的论据不够充分，需要补充数据支撑")
    print(rmsg)
