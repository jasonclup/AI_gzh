import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The file structure issue:
# 1. { "date": ..., "hourly_records": [ ... hour 10 data ... },
# 2.   "daily_summary": { OLD - with 30 high_ai_articles from hours 08-10 },
# 3.   "collected_at": "2026-04-12T10:54:00+08:00"  
# 4. }   <-- THIS INCORRECTLY CLOSES THE ROOT OBJECT
# 5. , { "hour": "11", ... }, { "hour": "12", ... } ...
# 6.   "daily_summary": { NEW },
# 7.   "collected_at": "2026-04-12T14:28:00+08:00"
# 8. }
#
# Fix: Remove lines 2-4 entirely (old daily_summary + old collected_at + spurious })
# Keep the array continuation into hour 11+

# Find the bad block: from "daily_summary" (the old one) to the } before ",    {""hour":11"
# 
# Step 1: Find the old daily_summary (first one, inside hourly_records area)
h10_pos = content.find('"hour": "10"')
# After hour 10's data ends, there's the old daily_summary
# Search for daily_summary after hour 10 position
old_ds_search_start = content.find('  "collected_at": "2026-04-12T10:54:00+08:00"', h10_pos)
print(f"Old collected_at (top-level) at: {old_ds_search_start}")

if old_ds_search_start > 0:
    # Go backwards to find start of this section (the daily_summary before it)
    # The pattern is: \n  "daily_summary": {\n    "total_hours": 3, ...\n    "high_ai_article_count": 30,\n    "high_ai_articles": [...long list...]\n  },\n  "collected_at": "..."
    
    # Find the daily_summary that precedes this collected_at
    search_area = content[max(0, old_ds_search_start-50000):old_ds_search_start]
    ds_in_area = search_area.rfind('"daily_summary"')
    if ds_in_area >= 0:
        old_ds_absolute = max(0, old_ds_search_start-50000) + ds_in_area
        print(f"Old daily_summary starts at: {old_ds_absolute}")
        
        # Now find where this bad block ends - after the collected_at line
        # It should be: \n}\n,\n    {\n      "hour": "11"
        after_col = content[old_ds_search_start:]
        
        # Find the }\n,\n    {\n      "hour": "11"
        end_match = re.search(r'\}\s*,\s*\{\s*\n\s*"hour":\s*"11"', after_col)
        if end_match:
            bad_end_abs = old_ds_search_start + end_match.end()
            print(f"Bad block ends at: {bad_end_abs}")
            
            # Remove everything from old_ds_absolute to bad_end_abs (inclusive of }\n)
            # But keep the ,\n    { for array continuation
            # Actually end_match includes up to "11" start, so we need to go back
            
            # Let me be more precise: 
            # Bad area = from old_ds_absolute to the } that closes root (before comma)
            close_brace_pos = content.rfind('}', old_ds_search_start, bad_end_abs)
            comma_after = content.find(',', close_brace_pos)
            
            print(f"Removing from {old_ds_absolute} to {comma_after+1}")
            
            # New content = before old_ds + from after the comma onwards
            new_content = content[:old_ds_absolute].rstrip() + content[comma_after+1:].lstrip()
            
            try:
                data = json.loads(new_content)
                hrs = len(data['hourly_records'])
                print(f"\n*** JSON FIXED! *** Hours: {hrs}")
                print(f"Topics: {data['daily_summary']['total_topics']}, Articles: {data['daily_summary']['total_articles']}")
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                sz = len(json.dumps(data, ensure_ascii=False)) / 1024
                print(f"Saved! Size: {sz:.1f} KB")
                
                # Cleanup temp files
                import os
                for tmp in ['_fix_json.py', '_fix_json2.py', '_fix_json3.py', '_fix_json4.py', '_fix_final.py', '_rebuild.py', '_fix_v5.py']:
                    tp = os.path.join(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher', tmp)
                    if os.path.exists(tp):
                        os.remove(tp)
                        print(f"Cleaned up {tmp}")
                        
            except json.JSONDecodeError as e:
                print(f"Error: {e}")
                with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_debug.json', 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("Debug saved")
        else:
            print("Could not find end pattern")
            print(f"After collected_at:\n{repr(after_col[:200])}")
    else:
        print("Could not find daily_summary in search area")
else:
    print("Old collected_at not found!")
