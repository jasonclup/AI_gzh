# -*- coding: utf-8 -*-
"""临时脚本：发送爆款分析飞书通知"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

result = json.load(open('output/analysis/2026-04-15_19-10-30_analysis.json', 'r', encoding='utf-8'))

from modules.feishu_bot import load_config, FeishuBot
config = load_config()
# Find coordinator bot
coord = None
for b in config.get('bots', []):
    if b.get('role') == 'coordinator':
        coord = b
        break
if not coord:
    # Fallback to first bot
    coord = config.get('bots', [{}])[0]
print(f"Using bot: {coord.get('name', 'unknown')} (role={coord.get('role')})")
bot = FeishuBot(app_id=coord['app_id'], app_secret=coord['app_secret'], name='viral_analysis')
chat_id = config.get('default_chat_id', '') or 'oc_cd6408709942d68abc3873cb7159e88c'

stats = result['stats']
plan = result['update_plan']
new_techs = plan.get('new_techniques_to_add', [])
priority = plan.get('priority_updates', [])

lines = []
lines.append("[爆款文章学习报告]")
lines.append("时间: 2026-04-15 19:10")
lines.append("")
lines.append("[分析概况]")
lines.append(f"  - 采集文章: {stats['articles_collected']}篇")
lines.append(f"  - 科技相关: {stats['tech_related']}篇")
lines.append(f"  - 高优更新: {len(priority)}条")
lines.append(f"  - 新增技巧: {len(new_techs)}个")

if new_techs:
    lines.append("")
    lines.append("[新发现的写作技巧 Top6]")
    for i, t in enumerate(new_techs[:6], 1):
        lines.append(f"  {i}. {t}")

if priority:
    lines.append("")
    lines.append("[本次更新的核心内容]")
    for p in priority[:3]:
        change_text = p.get("change", "")[:60]
        lines.append(f"  * {change_text}")

lines.append("")
lines.append("article_generator.py 已自动更新标记!")
lines.append("-- 来自爆款文章学习系统 v1.0")

msg = "\n".join(lines)
print("Sending message to Feishu...")
print("---MESSAGE START---")
print(msg)
print("---MESSAGE END---")

resp = bot.send_text(chat_id, msg)
print(f"Response: {resp}")
if resp.get('code') == 0:
    print("OK: Feishu notification sent!")
else:
    print(f"WARN: API returned: {resp}")
