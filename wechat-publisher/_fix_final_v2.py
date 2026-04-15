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
    except Exception as e:
        print(f"Parse error at {pos}: {e}")
        break

print(f"Parsed {len(objs)} objects:")
for i, o in enumerate(objs):
    if isinstance(o, dict):
        keys = list(o.keys())
        print(f"  [{i}] keys={keys[:10]}")
        # Check for total_hours
        if "total_hours" in o or "high_ai_articles" in o:
            print(f"       *** THIS IS DAILY SUMMARY! ***")

# Build final object
full_obj = {"date": obj["date"], "hourly_records": obj["hourly_records"].copy()}
hourly_records = full_obj["hourly_records"]

for o in objs:
    if isinstance(o, dict) and "hour" in o:
        hourly_records.append(o)
    elif isinstance(o, dict) and ("total_hours" in o or "overall_avg_ai_score" in o):
        full_obj["daily_summary"] = o
        print(f"Found daily_summary at index {objs.index(o)}!")

if "daily_summary" not in full_obj:
    # Build it manually
    hrs = len(hourly_records)
    total_topics = sum(len(h.get("hot_topics", [])) for h in hourly_records)
    total_articles = sum(t.get("analysis", {}).get("article_count", 0) for h in hourly_records for t in h.get("hot_topics", []))
    scores = [a.get("ai_score", 0) for h in hourly_records for t in h.get("hot_topics", []) for a in t.get("competitor_articles", [])]
    avg_score = round(sum(scores)/len(scores), 1) if scores else 0
    high_ai = sum(1 for s in scores if s > 70)
    
    high_ai_articles = []
    for h in hourly_records:
        for t in h.get("hot_topics", []):
            for a in t.get("competitor_articles", []):
                if a.get("ai_score", 0) > 70:
                    high_ai_articles.append({
                        "title": a.get("title", "")[:60],
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
    print(f"Built daily_summary manually: hours={hrs}, topics={total_topics}, articles={total_articles}")

full_obj["collected_at"] = "2026-04-12T14:28:00+08:00"

final = json.dumps(full_obj, ensure_ascii=False, indent=2)
v = json.loads(final)
ds = v['daily_summary']
print(f"\n*** FINAL: Hours={len(v['hourly_records'])}, Topics={ds['total_topics']}, Articles={ds['total_articles']}, AvgAI={ds['overall_avg_ai_score']}, HighAI>70={ds['high_ai_article_count']} ***")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(final)
sz = len(final)/1024
print(f"Saved! Size: {sz:.1f} KB")
