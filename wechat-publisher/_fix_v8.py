import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# From the debug output, before old daily_summary the content ends with:
# }\n      ]\n    }\n  ],\n  
# So hour 10 record ends with:    }\n  ],
# Then old daily_summary starts

# Find "  ],\n  \n  "daily_summary"" pattern
boundary = content.find('  ],\n  "\n  "daily_summary"')
if boundary < 0:
    # Try without extra newline
    boundary = content.find('  ],\n  "daily_summary"')

print(f"Boundary at: {boundary}")

if boundary > 0:
    # Everything up to and including "  ]," (the hourly_records array continues after this)
    # Actually "  ]," closes hot_topics of last topic in hour 10
    # Then "}" closes the hour 10 record
    # Let me check what's between ], and daily_summary
    
    between = content[boundary:boundary+50]
    print(f"At boundary: {repr(between)}")
    
    # The structure is:   },\n  ],\n  "daily_summary": 
    # We want to keep:   },\n  ],  (for array continuation)
    # And skip to: ,\n    {\n      "hour": "11"
    
    # Find hour 11
    h11 = content.find('"hour": "11"', boundary)
    
    # Build new: content[:up to after "  ],"] + ",\n    {" + [from h11's { onwards]
    
    # Find the { that opens hour 11 record
    h11_open = content.rfind('{', boundary, h11)
    
    new_content = content[:boundary+4].rstrip() + ',\n    ' + content[h11_open+1:].lstrip()
    
    try:
        data = json.loads(new_content)
        hrs = len(data['hourly_records'])
        print(f"\n*** JSON FIXED! Hours: {hrs} ***")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        sz = len(json.dumps(data, ensure_ascii=False)) / 1024
        print(f"Saved! Size: {sz:.1f} KB")
        print(f"Topics: {data['daily_summary']['total_topics']}, Articles: {data['daily_summary']['total_articles']}")
        
        import os
        for tmp in ['_debug_pos.py','_final_fix.py','_debug.json','_debug2.json','_fix_v7.py']:
            tp = os.path.join(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher', tmp)
            if os.path.exists(tp): os.remove(tp)
        print("Cleaned up!")
    except Exception as e:
        print(f"Error: {e}")
        with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_debug3.json','w',encoding='utf-8') as wf:
            wf.write(new_content)
else:
    print("Boundary not found. Trying manual extraction...")
    # Last resort: just extract the good parts manually based on known positions
    # Part 1: from start to end of hour 10 data (before old DS)
    # Part 2: from hour 11 start to end
    
    h10_end = content.find('  "collected_at": "2026-04-12T10:54:00+08:00"', 50650)  # hour 10 internal collected_at
    # After hour 10's collected_at, the rest of hour 10 data continues...
    # This is getting too complex. Let me use a different approach entirely.
    
    # Use json decoder with raw_decode to find valid JSON prefix
    decoder = json.JSONDecoder()
    try:
        obj, end = decoder.raw_decode(content)
        print(f"Valid JSON prefix length: {end}")
        print(f"This covers hours 08-10 with old summary")
        # The remaining content after `end` is our new data (with some garbage prefix)
        remaining = content[end:]
        print(f"Remaining ({len(remaining)} chars): {repr(remaining[:100])}")
    except Exception as e2:
        print(f"raw_decode error: {e2}")
