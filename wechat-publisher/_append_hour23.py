# -*- coding: utf-8 -*-
"""
追加第15轮 23:00 数据到主JSON文件
"""
import json
import os

DATA_FILE = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-11.json"
NEW_HOUR_FILE = r"C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\_hour_23.json"

# 读取主数据文件
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    main_data = json.load(f)

# 读取新生成的23:00数据
with open(NEW_HOUR_FILE, 'r', encoding='utf-8') as f:
    new_record = json.load(f)

# 追加到hourly_records
if 'hourly_records' not in main_data:
    main_data['hourly_records'] = []

main_data['hourly_records'].append(new_record)

# 更新最后时间
from datetime import datetime, timezone, timedelta
main_data['collected_at'] = datetime.now(timezone(timedelta(hours=8))).isoformat()

# 更新 daily_summary
total_articles = sum(
    len(hr.get('hot_topics', [])) * 3 
    for hr in main_data['hourly_records']
)
all_scores = []
high_ai_total = 0
for hr in main_data['hourly_records']:
    for topic in hr.get('hot_topics', []):
        for art in topic.get('competitor_articles', []):
            all_scores.append(art.get('ai_score', 0))
            if art.get('ai_score', 0) > 70:
                high_ai_total += 1

avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0

main_data['daily_summary'] = {
    "date": "2026-04-11",
    "total_hours": len(main_data['hourly_records']),
    "total_topics": sum(len(hr.get('hot_topics', [])) for hr in main_data['hourly_records']),
    "total_articles": len(all_scores),
    "average_ai_score": avg_score,
    "max_ai_score": max(all_scores) if all_scores else 0,
    "min_ai_score": min(all_scores) if all_scores else 0,
    "high_ai_count_70plus": high_ai_total,
    "high_ai_ratio_pct": round(high_ai_total / len(all_scores) * 100, 1) if all_scores else 0,
}

# 写回主文件
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(main_data, f, ensure_ascii=False, indent=2)

file_size = os.path.getsize(DATA_FILE)

print(f"=== 入库完成 ===")
print(f"总轮次: {len(main_data['hourly_records'])}")
print(f"总文章数: {len(all_scores)}")
print(f"累计平均AI评分: {avg_score}")
print(f"高AI文章总数(>70): {high_ai_total} ({main_data['daily_summary']['high_ai_ratio_pct']}%)")
print(f"数据文件大小: {file_size / 1024:.1f} KB")
