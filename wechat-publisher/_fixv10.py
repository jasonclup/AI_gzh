import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

decoder = json.JSONDecoder()
obj, end_pos = decoder.raw_decode(content)
remaining = content[end_pos:]

# Find start of hour 11 data
match = re.search(r'\{\s*"hour":\s*"11"', remaining)
if not match:
    print("ERROR: Cannot find hour 11!")
    exit(1)

clean = remaining[match.start():]

# Parse each top-level JSON object from clean
# Structure: {hour:11...}, {hour:12...}, {hour:13...}, {hour:14...}, {daily_summary...}, {collected_at...}
objs = []
pos = 0
while pos < len(clean):
    # Skip whitespace/newlines
    while pos < len(clean) and clean[pos] in ' \t\n\r,':
        pos += 1
    if pos >= len(clean):
        break
    
    try:
        o, new_end = decoder.raw_decode(clean[pos:])
        objs.append(o)
        pos += new_end
    except json.JSONDecodeError as e:
        print(f"Parse error at pos {pos}: {e}")
        print(f"Context: {repr(clean[pos:pos+100])}")
        break

print(f"Parsed {len(objs)} objects:")
for i, o in enumerate(objs):
    if isinstance(o, dict):
        keys = list(o.keys())[:5]
        print(f"  [{i}] type=dict keys={keys}...")
    else:
        print(f"  [{i}] type={type(o).__name__} value={str(o)[:80]}")

# Reconstruct
full_obj = {"date": obj["date"], "hourly_records": obj["hourly_records"].copy(), "daily_summary": None, "collected_at": None}

for o in objs:
    if isinstance(o, dict):
        if "hour" in o and o["hour"] in ["11","12","13","14"]:
            full_obj["hourly_records"].append(o)
        elif "total_hours" in o:
            full_obj["daily_summary"] = o
        elif "collected_at" in o and len(o) <= 2:
            full_obj["collected_at"] = o.get("collected_at")

final = json.dumps(full_obj, ensure_ascii=False, indent=2)
v = json.loads(final)
hrs = len(v['hourly_records'])
topics = v['daily_summary']['total_topics']
articles = v['daily_summary']['total_articles']
print(f"\n*** SUCCESS! Hours={hrs}, Topics={topics}, Articles={articles} ***")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(final)
print(f"Saved! Size: {len(final)/1024:.1f} KB")

import os
for tmp in ['_fixv9.py','_clean_remain.json']:
    tp = os.path.join(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher', tmp)
    if os.path.exists(tp): os.remove(tp)
print("Done!")
