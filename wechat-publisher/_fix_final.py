import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The file has this structure issue:
# 1. Normal data for hours 08, 09, 10 in hourly_records array
# 2. Then old: "daily_summary": {...}, "collected_at": "...", }  <-- closes the whole JSON object
# 3. Then new data appended: , { "hour": "11", ... }, { "hour": "12", ... }, ... 
# 4. Then new daily_summary and collected_at

# Fix: Remove step 2's closing and merge

# Find the OLD top-level daily_summary (the one that incorrectly closes the object)
# It's after hour 10's data ends (the last } of hour 10's hot_topics)

# Strategy: find all top-level structures
# The correct structure should be: { date, hourly_records: [...], daily_summary, collected_at }

# Let me find where the break is - there should be a } that closes the root object prematurely
# followed by more data

# Find the pattern: old daily_summary block
# It starts with \n  "daily_summary": { with lots of high_ai_articles entries

old_daily_summary_pattern = r'"high_ai_articles":\s*\[.*?"ai_score": 97'
matches = list(re.finditer(old_daily_summary_pattern, content))
print(f"Found {len(matches)} daily_summary patterns")

for i, m in enumerate(matches):
    print(f"  Match {i} at pos {m.start()}: ...{repr(content[m.start():m.start()+60])}")

if len(matches) >= 2:
    # First match is the old one (inside the broken part)
    # We need to remove from before the first daily_summary to after its closing }
    # Keep everything from hour 11 onwards
    
    # Find the start of old daily_summary section  
    # Go backwards to find the newline before it
    ds1_start = content.rfind('\n', 0, matches[0].start())
    
    # Find the end of old daily_summary + collected_at + closing }
    # Search forward from match[1] end (second daily_summary) to find what's between them
    
    # Actually simpler: find "collected_at": "2026-04-12T10:54:00+08:00"
    old_collected = content.find('2026-04-12T10:54:00+08:00"')
    # This is inside hour 10 record AND also at top level? Let me check
    all_old = [m.start() for m in re.finditer(r'2026-04-12T10:54:00\+08:00"', content)]
    print(f"\nFound '10:54:00' at positions: {all_old}")
    
    # The second occurrence should be the problematic top-level one
    if len(all_old) >= 2:
        bad_end = content.find('}', all_old[1]) + 1  # The } that closes root object
        print(f"Bad area: {ds1_start} to ~{bad_end}")
        print(f"Bad area content preview: {repr(content[ds1_start:ds1_start+100])}")
        
        # New approach: just extract valid portions
        # Part 1: from start to end of hour 10's data (before old daily_summary)
        # Part 2: from hour 11 to end of file
        
        part1 = content[:ds1_start].rstrip()
        
        # Find hour 11
        h11 = content.find('"hour": "11"')
        # Go back to find the array comma/brace
        pre_h11 = content.rfind(',', 0, h11)
        if pre_h11 > ds1_start:
            part2_start = pre_h11 + 1
            part2 = content[part2_start_start:].lstrip()
            
            # Remove leading } if it's a dangling close brace
            if part2.startswith('}'):
                nl = part2.find('\n')
                part2 = part2[nl+1:].lstrip()
            
            new_content = part1 + ',\n' + part2
            
            try:
                data = json.loads(new_content)
                print(f"\n*** JSON FIXED! ***")
                print(f"Hours: {len(data['hourly_records'])}")
                print(f"Topics: {data['daily_summary']['total_topics']}")
                print(f"Articles: {data['daily_summary']['total_articles']}")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                size = len(json.dumps(data, ensure_ascii=False)) / 1024
                print(f"Saved! File size: {size:.1f} KB")
            except Exception as e:
                print(f"\nError: {e}")
                with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_debug.json', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("Debug saved")
