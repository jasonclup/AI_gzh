import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The correct approach: find the exact boundary
# After hour 10's last article analysis }}, there should be ] to close hot_topics
# Then } to close the hour 10 record  
# Then , to continue hourly_records array
# But instead we have old daily_summary + collected_at + }

# Find hour 10's last competitor_article end
# Search backwards from old_ds_start (79029) for: }\n    ]\n  },\n
target_before = content[:79029]
print(f"Content before old DS (last 300 chars):")
print(repr(target_before[-300:]))

# The last thing before old daily_summary should be the closing of hour 10 record
# which looks like: \n    ]\n  },\n
idx = target_before.rfind(']\n  },')
if idx >= 0:
    print(f"\nFound hour 10 record end at relative pos {idx} (absolute {idx})")
    
    # Everything up to and including this } (the hour 10 closer)
    # Then skip everything until we find the start of hour 11 data
    
    # Hour 11 starts with "hour": "11"
    h11 = content.find('"hour": "11"', 79029)
    print(f"Hour 11 at: {h11}")
    
    # Go back from h11 to find the { or , that starts it
    pre_h11 = content.rfind(',\n    {', 79029, h11)
    if pre_h11 > 0:
        new_content = content[:idx+6] + ',\n    ' + content[pre_h11+2:].lstrip()
        
        try:
            data = json.loads(new_content)
            hrs = len(data['hourly_records'])
            print(f"\n*** SUCCESS! JSON FIXED! Hours: {hrs} ***")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            sz = len(json.dumps(data, ensure_ascii=False)) / 1024
            print(f"Saved! Size: {sz:.1f} KB")
            print(f"Topics: {data['daily_summary']['total_topics']}, Articles: {data['daily_summary']['total_articles']}")
            
            # Cleanup
            import os
            for tmp in ['_debug_pos.py','_final_fix.py','_debug.json']:
                tp = os.path.join(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher', tmp)
                if os.path.exists(tp): os.remove(tp)
            print("Done!")
        except Exception as e:
            print(f"Error: {e}")
            with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_debug2.json','w',encoding='utf-8') as wf:
                wf.write(new_content)
            print("Debug saved")
    else:
        print(f"No comma-brace found before h11. Pre-h11 area: {repr(content[h11-30:h11+30])}")
else:
    print("Could not find hour 10 record end pattern")
