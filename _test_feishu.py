# -*- coding: utf-8 -*-
"""测试飞书机器人Token连接"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher')
from modules.feishu_bot import FeishuTeam

team = FeishuTeam.from_config()
print("=" * 50)
print("  飞书AI团队 - Token连接测试")
print("=" * 50)

for key, bot in team.bots.items():
    try:
        token = bot.get_token()
        print(f"  OK {bot.name}: Token={token[:20]}...")
    except Exception as e:
        print(f"  FAIL {bot.name}: {e}")

print("\n全部完成!")
