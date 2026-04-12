# -*- coding: utf-8 -*-
import json

BACKUP = 'data/competitor_analysis/2026-04-11.json.bak'
TARGET = 'data/competitor_analysis/2026-04-11.json'

with open(BACKUP, 'r', encoding='utf-8') as f:
    raw = f.read()

raw = raw.replace('\n', ' ').replace('\r', '')

# The EXACT issue: ...视角提供独特见解"}]}], "daily_summary": ...
# There should be a comma after ] before "daily_summary"
# BUT also: the daily_summary object itself might be truncated
# Let's check what comes after daily_summary

ds_start = raw.find('"daily_summary"')
print(f"daily_summary at: {ds_start}")
print(f"Content after: {raw[ds_start:ds_start+200]}")

# Find where record 06 starts  
h06 = raw.find('"hour": "06"')
print(f"hour 06 at: {h06}")

# Get the daily_summary section (might be truncated)
ds_section = raw[ds_start:h06]
print(f"\nDaily summary section ({len(ds_section)} chars):")
print(ds_section[:500])

# Check if ds_section ends properly
print(f"\nLast 50 chars of ds: {repr(ds_section[-50:])}")

# The fix: the missing comma + possibly incomplete daily_summary
# Let's try just adding the comma first
fix1 = raw[:ds_start] + raw[ds_start:].replace(']}], "daily_summary"', '}]}],  "daily_summary"', 1)
try:
    data = json.loads(fix1)
    print("COMMA FIX WORKED!")
except json.JSONDecodeError as e:
    print(f"Comma fix failed: {e.msg} at {e.pos}")
    
    # Maybe daily_summary itself is incomplete/truncated
    # Let's replace the entire broken section with a clean one
    # Find: everything from start to right before daily_summary, 
    # then add clean daily_summary, then continue from hour 06
    
    before_ds = raw[:ds_start]
    
    # Check brace balance before daily_summary
    o = before_ds.count('{')
    c = before_ds.count('}')
    print(f"\nBraces before DS: open={o} close={c} diff={o-c}")
    
    # Build clean file
    new_file = (
        before_ds +
        ',  "daily_summary": {"total_topics_analyzed":10,"total_articles_collected":30,"avg_ai_score":39,"high_ai_ratio_topics":[],"key_findings":[],"high_ai_score_documents":[]}' +
        '},  {' +
        raw[h06+10:]  # skip leading {'"hour":"06"' since we added {
    )
    
    try:
        data = json.loads(new_file)
        print(f"REBUILD WORKED! Records: {len(data['hourly_records'])}")
        with open(TARGET, 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        print(f"Written to {TARGET}")
    except json.JSONDecodeError as e2:
        print(f"Rebuild failed: {e2.msg} at {e2.pos}")
        print(repr(new_file[max(0,e2.pos-40):e2.pos+40]))
        
        # Last resort: write a completely fresh file with only records 06 and 07
        # then we can append our new 08 record
        print("\n--- Last resort: extracting records 06 and 07 only ---")
        
        # Find record 07
        h07 = raw.find('"hour": "07"')
        print(f"Hour 07 at: {h07}")
        
        if h07 > 0:
            rec06_data = raw[h06:h07]
            rec07_data = raw[h07:]
            
            # Try parsing each separately by wrapping them
            for label, rec_data in [("06", rec06_data), ("07", rec07_data)]:
                wrapped = '{"date":"2026-04-11","hourly_records":[{"dummy":1,' + rec_data[10:] + '}]}'
                try:
                    td = json.loads(wrapped)
                    print(f"Record {label}: PARSED OK")
                except Exception as ex:
                    print(f"Record {label}: FAILED - {ex.msg}")
