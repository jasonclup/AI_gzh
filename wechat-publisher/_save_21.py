# -*- coding: utf-8 -*-
import json, os

with open('data/competitor_analysis/2026-04-12.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('_temp_21.json', 'r', encoding='utf-8') as f:
    new_record = json.load(f)

data['hourly_records'].append(new_record)
data['collected_at'] = new_record['collected_at']

total_topics = sum(len(r.get('hot_topics', [])) for r in data['hourly_records'])
total_articles_all = 0
all_scores = []
high_ai_total = 0
for r in data['hourly_records']:
    for t in r.get('hot_topics', []):
        for a in t.get('competitor_articles', []):
            total_articles_all += 1
            all_scores.append(a.get('ai_score', 0))
            if a.get('ai_score', 0) > 70:
                high_ai_total += 1

avg_all = sum(all_scores) / len(all_scores) if all_scores else 0

data['daily_summary'] = {
    'total_hours': len(data['hourly_records']),
    'total_topics': total_topics,
    'total_articles': total_articles_all,
    'overall_avg_ai_score': round(avg_all, 1),
    'high_ai_article_count': high_ai_total,
    'high_ai_ratio': f'{round(high_ai_total/max(total_articles_all,1)*100, 1)}%',
    'hour_coverage': [r['hour'] for r in data['hourly_records']],
}

with open('data/competitor_analysis/2026-04-12.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

size_kb = os.path.getsize('data/competitor_analysis/2026-04-12.json') / 1024

print(f'=== 数据追加完成 ===')
print(f'total hourly_records: {len(data["hourly_records"])}')
print(f'总热点: {total_topics}')
print(f'总文章: {total_articles_all}')
print(f'综合平均AI评分: {avg_all:.1f}')
print(f'高AI文章(>70): {high_ai_total}篇 ({round(high_ai_total/max(total_articles_all,1)*100,1)}%)')
print(f'覆盖时段: {[r["hour"] for r in data["hourly_records"]]}')
print(f'数据文件: {size_kb:.1f}KB')
