import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The structure issue:
# After hour 10's data ends with:   }\n  },\n  "collected_at": "2026-04-12T10:54:00+08:00"\n},\n    {
#       "hour": "11", ...
#
# We need to remove: \n  "collected_at": "2026-04-12T10:54:00+08:00"\n},\n
# And keep the },\n    { for continuing the array

# Find the exact bad pattern
bad_pattern = '  "collected_at": "2026-04-12T10:54:00+08:00"\n},\n    {'

if bad_pattern in content:
    # Replace it with just the array continuation
    new_content = content.replace(bad_pattern, ',\n    {')
    
    try:
        data = json.loads(new_content)
        hours = len(data['hourly_records'])
        print(f"JSON VALID! Hours={hours}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        size = len(json.dumps(data, ensure_ascii=False)) / 1024
        print(f"Saved! File size: {size:.1f} KB")
        print(f"Topics: {data['daily_summary']['total_topics']}, Articles: {data['daily_summary']['total_articles']}")
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
else:
    print("Pattern not found exactly, trying alternative...")
    # Try to find and debug
    idx = content.find('"collected_at": "2026-04-12T10:54:00+08:00"')
    if idx > 0:
        print(f"Found collected_at at {idx}:")
        print(repr(content[idx-20:idx+80]))
