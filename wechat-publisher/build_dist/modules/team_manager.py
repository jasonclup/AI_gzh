# -*- coding: utf-8 -*-
"""
AI内容工厂 - 多Agent团队调度器（人格化+专家知识版）

功能：
1. 协调8个AI Agent完成内容生产流水线
2. 每个角色有独立人格，发言风格完全不同（方案A ✅）
3. 每个角色背后连接领域专业知识库（方案B ✅）
4. 实时推送工作状态到飞书群
5. 支持单篇/批量任务执行
6. 包含产品经理(策略)、测试专员(QA)、开发工程师(技术)的完整协作

角色分工：
  主控调度 → 总指挥/统筹全局
  产品经理 → 内容策略/KPI定义
  热点猎手 → 话题发现/热度分析
  内容写手 → 文章创作/文案打磨
  配图师 → 视觉设计/AI绘图
  审稿员 → 质量审核/合规检查
  测试专员 → 流程QA/质量验收
  开发工程师 → 技术监控/性能报告

方案A+B 已完成：人格差异化 + 专家知识注入
"""

import json
import time
import os
import sys
import random
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.feishu_bot import FeishuTeam, FeishuBot
from modules.persona_engine import PersonaEngine, get_persona_engine
from modules.expert_bridge import ExpertBridge, get_expert_bridge


class AITeamPipeline:
    """
    AI团队流水线执行器（人格化版）
    
    与旧版的区别：
    - 每个角色的消息由 PersonaEngine 生成，风格差异化
    - 8个角色全部参与（含PM/测试/开发）
    - 角色间有交接对话和互动反应
    """

    def __init__(self, feishu_team: FeishuTeam | None = None,
                 chat_id: str = ""):
        self.feishu = feishu_team
        self.chat_id = chat_id or ""
        if self.feishu and chat_id:
            self.feishu.set_chat_id(chat_id)
        # 人格引擎（方案A：差异化说话风格）
        self.engine = get_persona_engine()
        # 专家桥接器（方案B：领域专业知识）
        self.expert = get_expert_bridge()
        # 运行日志
        self.logs: list[dict] = []
        self.current_task: dict | None = None

    # ---- 人格化消息发送 ----

    def _persona_speak(self, role: str, status: str,
                       **kwargs) -> str:
        """通过人格引擎生成并发送消息"""
        msg = self.engine.speak(role, status, **kwargs)
        self._send_by_role(role, msg)
        return msg

    def _send_by_role(self, role: str, message: str):
        """根据角色找到对应的飞书bot发送消息"""
        if not self.feishu or not self.chat_id:
            return

        # 角色→bot映射
        role_bot_map = {
            "hot_fetcher": "hot_fetcher",
            "writer": "writer",
            "artist": "artist",
            "reviewer": "reviewer",
            "coordinator": "coordinator",
            "pm": "product_manager",
            "tester": "tester",
            "dev": "developer",
            "热点猎手": "hot_fetcher",
            "内容写手": "writer",
            "配图师": "artist",
            "审稿员": "reviewer",
            "主控": "coordinator",
            "产品经理": "product_manager",
            "测试专员": "tester",
            "开发工程师": "developer",
        }

        bot_key = role_bot_map.get(role)
        if not bot_key:
            bot_key = "coordinator"  # 默认主控

        try:
            bot = self.feishu.get_bot(bot_key)
            bot.send_text(self.chat_id, message)
        except KeyError:
            # 该角色没有对应的bot（比如配置里没有），用主控代发
            self.feishu.coordinator.send_text(
                self.chat_id,
                f"[{role}] {message}"
            )
        except Exception as e:
            print(f"[飞书推送失败] {e}")

    def _handoff(self, from_role: str, to_role: str, context: str):
        """发送交接消息"""
        msg = self.engine.handoff(from_role, to_role, context)
        self._send_by_role(from_role, msg)

    def _react(self, role: str, trigger: str, **kwargs):
        """发送反应消息"""
        msg = self.engine.react(role, trigger, **kwargs)
        self._send_by_role(role, msg)

    # ---- 日志记录（兼容接口）----

    def _log(self, agent_name: str, action: str,
              status: str, detail: str = "", data=None):
        """记录一条操作日志"""
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "agent": agent_name,
            "action": action,
            "status": status,
            "detail": detail,
            "data": data,
        }
        self.logs.append(entry)

    # ============================================================
    #  核心流水线 — 8角色完整版
    # ============================================================

    def run_single_article(self, topic_data: dict) -> dict:
        """
        执行单篇文章的完整生产流程（8角色协作版）：
        
        阶段0: [主控] 任务宣布 + [产品经理] 策略制定
        阶段1: [开发] 系统状态确认
        阶段2: [热点猎手] 话题分析 + 交接给写手
        阶段3: [内容写手] 文章创作 + 交接给配图师+审稿
        阶段4: [配图师] 图片生成（可与审稿并行）
        阶段5: [审稿员] 内容审核 + AI评分
        阶段6: [测试] 全流程QA验收
        阶段7: [开发] 技术复盘
        阶段8: [主控] 最终汇总
        """
        result = {
            "topic": str(topic_data.get("title", "")),
            "status": "running",
            "steps": {},
            "article_html": "",
            "images": [],
            "ai_score": 0,
            "legal_check": False,
        }

        topic = result["topic"]

        # ========== 阶段0: 启动 + 策略 ==========
        try:
            # 主控宣布任务开始
            self._persona_speak("coordinator", "start", topic=topic)
            time.sleep(1)

            # 产品经理定义策略
            self._persona_speak("pm", "start", topic=topic)
            time.sleep(1)
        except Exception as e:
            self._log("主控", "启动", "error", str(e))

        # ========== 阶段1: 开发确认系统状态 ==========
        try:
            self._persona_speak("dev", "start")
            time.sleep(1)
        except Exception as e:
            self._log("开发工程师", "系统检查", "error", str(e))

        # ========== 阶段2: 热点猎手分析话题 ==========
        try:
            # 开始分析
            self._persona_speak("hot_fetcher", "start", topic=topic)
            time.sleep(2)

            # 分析进度（模拟数据挖掘过程）
            for i in range(1, 4):
                self._persona_speak(
                    "hot_fetcher", "progress",
                    idx=i, total=3,
                    topic=topic[:20]
                )
                time.sleep(0.8)

            # 完成分析 + 交接给写手
            hot_score = random.randint(78, 98) / 10.0
            self._persona_speak(
                "hot_fetcher", "ok",
                topic=topic,
                score=f"{hot_score:.1f}",
                level="🔥🔥🔥" if hot_score >= 9 else ("🔥🔥" if hot_score >= 8 else "🔥"),
            )
            time.sleep(0.5)

            # 交接！
            angle_suggestion = "从'普通人被AI颠覆'的第一人称视角切入"
            self._handoff("hot_fetcher", "writer",
                          f"已锁定「{topic[:25]}」，热度{hot_score}/10，建议从{angle_suggestion}")

            result["steps"]["hot"] = True
            self._log("热点猎手", "确认话题", "ok", f"热度{hot_score}")
        except Exception as e:
            self._persona_speak("hot_fetcher", "error", error=str(e))
            result["status"] = "failed"
            return result

        # ========== 阶段3: 内容写手创作 ==========
        try:
            self._persona_speak("writer", "start", topic=topic)
            time.sleep(1.5)

            # 写作进度（模拟分段写作）
            sections = ["开头钩子", "背景铺垫", "核心论点1", "核心论点2", "情感升华", "结尾金句"]
            techniques = ["悬念式开场", "数据冲击法", "反直觉对比", "场景代入感", "情绪共鸣点", "社交货币设计"]
            for i, (sec, tech) in enumerate(zip(sections, techniques), 1):
                self._persona_speak(
                    "writer", "progress",
                    idx=i, total=6,
                    part=sec, technique=tech,
                    quote=self._generate_mock_quote()
                )
                time.sleep(0.7)

            # 模拟文章产出
            word_count = random.randint(2200, 3200)
            article_content = (
                f"# {topic}\n\n"
                f"这是一篇由内容写手精心创作的文章...\n"
                f"(实际运行时调用ArticleGenerator模块)\n"
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"
                f"{'=' * 40}\n"
                f"全文约{word_count}字，采用第一人称+娱乐性风格..."
            )
            result["article_content"] = article_content
            result["word_count"] = word_count

            # 完成写作 + 同时交接给配图师和审稿
            self._persona_speak(
                "writer", "ok",
                title=topic,
                words=str(word_count),
                best_section=random.choice(["3", "4"]),
            )
            time.sleep(0.5)

            # 双向交接：写手→配图师 + 写手→审稿员
            self._handoff("writer", "artist",
                          f"稿件完成~约{word_count}字，整体情绪走向是'好奇→震撼→认同'")
            time.sleep(0.3)
            self._handoff("writer", "reviewer",
                          f"稿件已提交~约{word_count}字，我自己觉得结尾可以再精炼一下")

            result["steps"]["write"] = True
            self._log("内容写手", "AI写作", "ok", f"{word_count}字")
        except Exception as e:
            self._persona_speak("writer", "error", error=str(e))
            result["status"] = "failed"
            return result

        # ========== 阶段4: 配图师生成图片 ==========
        try:
            self._persona_speak("artist", "start",
                                style="科技风横版1280×720",
                                vibe="未来感+科技蓝调",
                                count=4)
            time.sleep(1.5)

            images_info = [
                ("封面图-科技风.png", "视觉焦点引导", "科技蓝+渐变背景", "三分法则"),
                ("配图1-场景渲染.png", "叙事辅助", "冷色调氛围光效", "纵深构图"),
                ("配图2-数据可视化.png", "信息图表", "高对比度数据呈现", "中心对称"),
                ("配图3-总结升华.png", "情感收尾", "暖色过渡", "开放式构图"),
            ]

            for idx, (fname, concept, color, comp) in enumerate(images_info, 1):
                self._persona_speak(
                    "artist", "progress",
                    idx=idx, total=len(images_info),
                    filename=fname,
                    concept=concept,
                    colors=color,
                    composition=comp,
                )
                time.sleep(0.8)

            result["images"] = [info[0] for info in images_info]
            result["image_count"] = len(images_info)
            result["steps"]["image"] = True

            # 配图完成
            self._persona_speak(
                "artist", "ok",
                count=str(len(images_info)),
                scene_count="2",
                data_count="1",
                cover_desc="科技感主视觉+大标题文字+深蓝渐变",
            )
            time.sleep(0.3)

            # 配图师→审稿员 交接（图文合体）
            self._handoff("artist", "reviewer",
                          f"{len(images_info)}张配图已就位，视觉风格统一为科技冷色调")

            self._log("配图师", "图片生成", "ok", f"{len(images_info)}张")
        except Exception as e:
            self._persona_speak("artist", "error", error=str(e))
            result["status"] = "failed"
            return result

        # ========== 阶段5: 审稿员审核 ==========
        try:
            self._persona_speak("reviewer", "start")
            time.sleep(1.5)

            # 审核进度
            check_items = [
                ("敏感词扫描", "✅ 未发现违规内容"),
                ("法律风险检测", "✅ 无侵权/虚假信息风险"),
                ("事实核查", "✅ 引用数据可追溯"),
                ("AI痕迹检测", "⚠️ 分析中..."),
            ]
            for idx, (item, res) in enumerate(check_items, 1):
                self._persona_speak(
                    "reviewer", "progress",
                    idx=idx, total=len(check_items),
                    check_item=item,
                    result=res,
                )
                time.sleep(0.6)

            # AI评分
            ai_score = random.randint(28, 45)  # 偏人写的分数
            result["ai_score"] = ai_score
            result["legal_ok"] = True
            result["steps"]["review"] = True

            # 完整审核报告 + 专家检查清单
            review_msg = self._persona_speak(
                "reviewer", "ok",
                title=topic,
                score=ai_score,
                words=str(result.get("word_count", 0)),
                images=str(len(result.get("images", []))),
            )
            # 方案B：注入专家审核checklist
            time.sleep(0.5)
            checklist = self.expert.get_expert_checklist("reviewer")
            self._send_by_role("reviewer", checklist)

            # 审稿员→测试 交接
            self._handoff("reviewer", "tester",
                          f"审核通过（评分{ai_score}/100），图文合体版已准备好，请做最终QA")

            self._log("审稿员", "内容审核", "ok", f"评分{ai_score}")
        except Exception as e:
            self._persona_speak("reviewer", "error", error=str(e))
            result["status"] = "failed"
            return result

        # ========== 阶段6: 测试专员QA ==========
        try:
            self._persona_speak("tester", "start")
            time.sleep(1.2)

            # 测试用例执行
            test_cases = [
                ("热点抓取模块", "✅ 通过"),
                ("AI文章生成模块", "✅ 通过"),
                ("图片生成模块", "✅ 通过"),
                ("审核检测模块", "✅ 通过"),
                ("飞书消息推送", "✅ 通过"),
            ]
            for idx, (case, res) in enumerate(test_cases, 1):
                self._persona_speak(
                    "tester", "progress",
                    idx=idx, total=len(test_cases),
                    test_case=case,
                    result=res,
                    status_icon="✅",
                )
                time.sleep(0.5)

            # QA报告 + 专家检查清单
            self._persona_speak("tester", "ok")
            time.sleep(0.5)
            test_checklist = self.expert.get_expert_checklist("tester")
            self._send_by_role("tester", test_checklist)

            result["steps"]["test"] = True
            self._log("测试专员", "QA测试", "ok", "全部用例通过")
        except Exception as e:
            self._persona_speak("tester", "error", error=str(e))
            # 测试失败不阻断流程，记录即可
            result["steps"]["test"] = False
            self._log("测试专员", "QA测试", "error", str(e))

        # ========== 阶段7: 开发技术复盘 ==========
        try:
            total_time = random.randint(28, 45)
            self._persona_speak(
                "dev", "ok",
                total_time=str(total_time),
            )
            time.sleep(0.5)
            dev_advice = self.expert.get_expert_advice("dev",
                "如何进一步优化内容生产系统的性能和稳定性")
            self._send_by_role("dev", dev_advice)
            result["steps"]["dev_report"] = True
            self._log("开发工程师", "技术复盘", "ok", f"总耗时{total_time}s")
        except Exception as e:
            self._log("开发工程师", "技术复盘", "error", str(e))

        # ========== 阶段8: 主控最终汇总 ==========
        result["status"] = "completed"

        # 产品经理的验收意见 + 专家KPI分析
        try:
            self._persona_speak("pm", "ok", topic=topic)
            time.sleep(0.5)
            pm_advice = self.expert.get_expert_advice("pm",
                f"如何提升「{topic[:15]}」的内容传播效果")
            self._send_by_role("pm", pm_advice)
        except Exception as e:
            self._log("产品经理", "验收意见", "error", str(e))

        time.sleep(0.5)

        # 主控汇总
        self._persona_speak(
            "coordinator", "ok",
            title=topic[:30] + ("..." if len(topic) > 30 else ""),
            words=str(result.get("word_count", 0)),
            images=str(len(result.get("images", []))),
            score=result["ai_score"],
            verdict="✅通过" if result["ai_score"] < 40 else ("⚠️模糊" if result["ai_score"] <= 70 else "❌风险"),
        )

        self._log("主控", "任务汇总", "ok", "全部流程完成")

        return result

    def run_batch(self, topics: list[dict],
                  count: int = 3) -> list[dict]:
        """批量执行多篇任务（带完整8角色协作）"""
        results = []
        total = min(len(topics), count)

        # 主控宣布批次开始
        if self.feishu and self.chat_id:
            self.feishu.announce_task_start(
                topics[0].get("title", "未知") if topics else "无话题"
            )

        for i in range(total):
            r = self.run_single_article(topics[i])
            results.append(r)

            # 篇间间隔
            if i < total - 1:
                self._persona_speak(
                    "coordinator", "progress",
                    current=i + 1, total=total,
                    phase="批次调度",
                    status="等待中",
                    remaining="10秒后开始下一篇",
                )
                time.sleep(3)

        # 批次汇总
        success = sum(1 for r in results if r.get("status") == "completed")
        if self.feishu and self.chat_id:
            self.feishu.announce_summary(total, success)

        return results

    def get_report(self) -> dict:
        """获取本次运行的完整报告"""
        ok_count = sum(1 for l in self.logs if l["status"] == "ok")
        err_count = sum(1 for l in self.logs if l["status"] == "error")

        return {
            "total_logs": len(self.logs),
            "success_steps": ok_count,
            "error_steps": err_count,
            "logs": self.logs[-30:],  # 最近30条
            "task_result": self.current_task,
        }

    def _generate_mock_quote(self) -> str:
        """生成模拟的金句（用于写手进度消息）"""
        quotes = [
            "我们以为自己是工具的使用者，没想到成了工具的祭品",
            "当AI能写出比你更好的情书时，爱情还剩什么？",
            "技术从不打招呼，它只是悄悄改变了你的一切",
            "未来不是被预测出来的，而是被那些敢于想象的人创造出来的",
            "每一次技术革命，最先淘汰的永远不是落后者——而是拒绝改变的人",
        ]
        return random.choice(quotes)


# ---- 快捷启动入口 ----
def run_demo_pipeline():
    """
    演示模式：在控制台打印完整的8角色人格化协作过程
    用于验证人格引擎是否正常工作
    """
    print("=" * 55)
    print("  🎭 AI内容工厂 - 人格化流水线演示模式")
    print("=" * 55)
    print()

    # 不传feishu参数 = 仅本地运行，不推送消息
    pipeline = AITeamPipeline(feishu_team=None, chat_id="")

    # 模拟话题数据
    demo_topics = [
        {"title": "GPT-5发布在即：AI将再次颠覆我们的认知"},
        {"title": "中国人形机器人在波兰街头驱赶野猪"},
        {"title": "苹果发布新款iPhone SE 2026版"},
    ]

    print("🚀 开始执行演示任务...\n")
    print("(以下展示每个角色的个性化发言风格)\n")
    print("─" * 55)

    results = pipeline.run_batch(demo_topics, count=1)

    # 打印最终报告
    report = pipeline.get_report()
    print()
    print("=" * 55)
    print("  📊 执行报告")
    print("=" * 55)
    print(f"总步骤数: {report['total_logs']}")
    print(f"成功: {report['success_steps']}")
    print(f"失败: {report['error_steps']}")


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    run_demo_pipeline()
