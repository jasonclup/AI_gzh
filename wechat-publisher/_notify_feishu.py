"""手动补发飞书通知 - 20:13 分析结果"""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

with open('output/analysis/2026-04-15_20-13-23_analysis.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

from modules.feishu_bot import load_config, FeishuBot

config = load_config()

# coordinator 可能在 bots 列表中
coord = config.get('coordinator', {})
if not coord:
    for bot in config.get('bots', []):
        if bot.get('role') == 'coordinator':
            coord = bot
            break

if coord.get('app_id') and coord.get('app_secret'):
    bot = FeishuBot(app_id=coord['app_id'], app_secret=coord['app_secret'], name='爆款分析')
    chat_id = config.get('CHAT_ID', '') or 'oc_cd6408709942d68abc3873cb7159e88c'

    stats = result['stats']
    plan = result['update_plan']
    new_techs = plan.get('new_techniques_to_add', [])
    priority = plan.get('priority_updates', [])

    lines = [
        '📊 爆款文章学习报告（第7次）',
        f'⏰ 时间：{result["run_time"]}',
        '',
        '📈 分析概况:',
        f'  • 采集文章: {stats["articles_collected"]}篇',
        f'  • 科技相关: {stats["tech_related"]}篇',
        f'  • 生活分享类(自述): {stats.get("life_share_count", 0)}篇',
        f'  • 高优更新: {len(priority)}条',
        f'  • 新增技巧: {len(new_techs)}个',
    ]
    if new_techs:
        lines.append('')
        lines.append('✨ 新发现的写作技巧:')
        for i, t in enumerate(new_techs[:8], 1):
            lines.append(f'  {i}. {t}')
    if priority:
        lines.append('')
        lines.append('🔧 本次核心更新:')
        for p in priority[:4]:
            lines.append(f'  • {p.get("change", "")[:60]}')

    lines.extend([
        '',
        '💡 article_generator.py 已手动补录更新!',
        '— 来自爆款学习系统 v1.0'
    ])

    msg = '\n'.join(lines)
    resp = bot.send_text(chat_id, msg)
    print(f'[OK] 飞书通知发送成功! code={resp.get("code")}, msg_id={resp.get("data",{}).get("message_id","N/A")}')
else:
    print('[SKIP] coordinator配置缺失，无法发送通知')
