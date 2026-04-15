import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

decoder = json.JSONDecoder()
obj, end_pos = decoder.raw_decode(content)
print(f"Valid JSON ends at: {end_pos}, has {len(obj.get('hourly_records',[]))} records")

remaining = content[end_pos:]
print(f"Remaining: {repr(remaining[:150])}")

match = re.search(r'\{\s*"hour":\s*"11"', remaining)
if match:
    clean_remaining = remaining[match.start():]
    extra_list = json.loads('[' + clean_remaining + ']')
    print(f"Extra list: {len(extra_list)} items")
    
    full_obj = {"date": obj["date"], "hourly_records": [], "daily_summary": None, "collected_at": None}
    full_obj["hourly_records"] = obj["hourly_records"].copy()
    
    if len(extra_list) > 0:
        last = extra_list[-1]
        if isinstance(last, dict) and "total_hours" in last:
            full_obj["daily_summary"] = last
            extra_list = extra_list[:-1]
        if len(extra_list) > 0:
            pl = extra_list[-1]
            if isinstance(pl, dict) and "collected_at" in pl and "total_hours" not in pl:
                full_obj["collected_at"] = pl["collected_at"]
                extra_list = extra_list[:-1]
        full_obj["hourly_records"].extend(extra_list)
    
    final = json.dumps(full_obj, ensure_ascii=False, indent=2)
    v = json.loads(final)
    print(f"\n*** SUCCESS! Hours: {len(v['hourly_records'])}, Topics: {v['daily_summary']['total_topics']}, Articles: {v['daily_summary']['total_articles']} ***")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final)
    print(f"Saved! Size: {len(final)/1024:.1f} KB")
else:
    print("Hour 11 pattern not found!")
