# -*- coding: utf-8 -*-
"""
飞书人格化消息推送测试
8个角色以各自独立人格发送差异化消息到飞书群
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 添加项目路径
sys.path.insert(0, r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher')

from modules.feishu_bot import FeishuTeam
from modules.team_manager import AITeamPipeline

print("=== 飞书人格化团队测试 ===")
print()

# 初始化飞书团队
team = FeishuTeam.from_config()
chat_id = team.config.get("default_chat_id", "")
team.set_chat_id(chat_id)

print(f"Chat ID: {chat_id}")
print(f"Bots: {list(team.bots.keys())}")
print()

# 创建人格化流水线
pipeline = AITeamPipeline(feishu_team=team, chat_id=chat_id)

# 模拟话题
test_topic = {"title": "GPT-5发布在即：AI将再次颠覆我们的认知"}

print(f"开始执行: {test_topic['title']}")
print("-" * 40)

result = pipeline.run_single_article(test_topic)

print()
print("=" * 40)
print(f"最终状态: {result['status']}")
print(f"AI评分: {result.get('ai_score', 0)}")
print(f"步骤: {list(result.get('steps', {}).keys())}")
print()
print("✅ 测试完成！请查看飞书群消息。")
