import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Known positions from analysis:
# - Old daily_summary starts at: 79029
# - Bad collected_at at: 84658 (value: "2026-04-12T10:54:00+08:00")
# - Hour 11 data starts right after with ,\n    {

old_ds_start = 79029  # \n  "daily_summary": {
bad_collected_at = 84658  # "collected_at": "2026-04-12T10:54:00+08:00"

# The bad block is from old_ds_start to after the } that closes root (before the comma before hour 11)
# After "2026-04-12T10:54:00+08:00" there should be "\n},\n    {"
after_bad = content[bad_collected_at:]
print(f"After bad collected_at: {repr(after_bad[:50])}")

# Find },\n that closes root object
close_pos = after_bad.find('}\n')
if close_pos >= 0:
    comma_pos = after_bad.find(',', close_pos)
    if comma_pos >= 0:
        bad_end_absolute = bad_collected_at + comma_pos + 1
        print(f"Bad block ends at: {bad_end_absolute}")
        
        # New content = everything before old daily_summary + from comma onwards (which is ,\n    {\n      "hour": "11")
        new_content = content[:old_ds_start].rstrip() + content[bad_end_absolute:].lstrip()
        
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
            for tmp in ['_debug_pos.py', '_fix_json.py', '_fix_json2.py', '_fix_json3.py', 
                       '_fix_json4.py', '_fix_final.py', '_rebuild.py', '_fix_v5.py',
                       '_fix_v6.py', '_fix_json4.py']:
                tp = os.path.join(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher', tmp)
                if os.path.exists(tp):
                    os.remove(tp)
            print("Cleaned up temp files")
            
        except Exception as e:
            print(f"Error: {e}")
            with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_debug.json', 'w', encoding='utf-8') as wf:
                wf.write(new_content)
            print("Debug saved")
