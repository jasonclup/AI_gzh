import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

decoder = json.JSONDecoder()
obj, end_pos = decoder.raw_decode(content)
remaining = content[end_pos:]
match = re.search(r'\{\s*"hour":\s*"11"', remaining)
clean = remaining[match.start():]

objs = []
pos = 0
while pos < len(clean):
    while pos < len(clean) and clean[pos] in ' \t\n\r,':
        pos += 1
    if pos >= len(clean):
        break
    try:
        o, new_end = decoder.raw_decode(clean[pos:])
        objs.append(o)
        pos += new_end
    except:
        break

print(f"Parsed {len(objs)} objects:")
for i, o in enumerate(objs):
    if isinstance(o, dict):
        print(f"  [{i}] keys={list(o.keys())[:8]}")
        if i >= 4:  # Print full for last 2
            print(f"       all_keys={list(o.keys())}")

# The last 2 objects should be daily_summary and the final wrapper
# Let's just manually handle this
full_obj = {"date": obj["date"], "hourly_records": obj["hourly_records"].copy()}

for o in objs:
    if isinstance(o, dict) and "hour" in o:
        full_obj["hourly_records"].append(o)

# Find daily_summary (the one with total_hours key, should be 5th object or later)
for o in objs[-3:]:
    if isinstance(o, dict) and "total_hours" in o:
        full_obj["daily_summary"] = o
        # Update it
        hrs = len(full_obj["hourly_records"])
        total_topics = sum(len(h.get("hot_topics", [])) for h in full_obj["hourly_records"])
        total_articles = sum(t.get("analysis", {}).get("article_count", 0) for h in full_obj["hourly_records"] for t in h.get("hot_topics", []))
        
        scores = [a.get("ai_score", 0) for h in full_obj["hourly_records"] for t in h.get("hot_topics", []) for a in t.get("competitor_articles", [])]
        avg_score = round(sum(scores)/len(scores), 1) if scores else 0
        high_ai = sum(1 for s in scores if s > 70)
        
        high_ai_articles = []
        for h in full_obj["hourly_records"]:
            for t in h.get("hot_topics", []):
                for a in t.get("competitor_articles", []):
                    if a.get("ai_score", 0) > 70:
                        high_ai_articles.append({
                            "title": a.get("title", ""),
                            "account": a.get("account", ""),
                            "ai_score": a.get("ai_score", 0),
                            "topic": t.get("topic", "")
                        })
        
        full_obj["daily_summary"] = {
            "total_hours": hrs,
            "total_topics": total_topics,
            "total_articles": total_articles,
            "overall_avg_ai_score": avg_score,
            "high_ai_article_count": high_ai,
            "high_ai_articles": high_ai_articles[:30]
        }
        break

full_obj["collected_at"] = "2026-04-12T14:28:00+08:00"

final = json.dumps(full_obj, ensure_ascii=False, indent=2)
v = json.loads(final)
print(f"\n*** Hours={len(v['hourly_records'])}, Topics={v['daily_summary']['total_topics']}, Articles={v['daily_summary']['total_articles']} ***")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(final)
print(f"Saved! Size: {len(final)/1024:.1f} KB")
import os
for tmp in ['_fixv10.py']:
    tp = os.path.join(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher', tmp)
    if os.path.exists(tp): os.remove(tp)
print("Done!")
