import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# The exact bad string between hour 10 data and hour 11 data:
#   },\n  "collected_at": "2026-04-12T10:54:00+08:00"\n},\n    {
# Replace with just: ,\n    {

bad = '  },\n  "collected_at": "2026-04-12T10:54:00+08:00"\n},\n    {'
good = ',\n    {'

if bad in content:
    new_content = content.replace(bad, good)
    
    # Verify it also doesn't have the old daily_summary issue
    # Check for duplicate daily_summary
    ds_count = new_content.count('"daily_summary"')
    print(f"daily_summary count: {ds_count}")
    
    try:
        data = json.loads(new_content)
        print(f"*** JSON FIXED! ***")
        print(f"Hours: {len(data['hourly_records'])}")
        print(f"Topics: {data['daily_summary']['total_topics']}")
        print(f"Articles: {data['daily_summary']['total_articles']}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        size = len(json.dumps(data, ensure_ascii=False)) / 1024
        print(f"Saved successfully! Size: {size:.1f} KB")
    except json.JSONDecodeError as e:
        print(f"Error: {e}")
else:
    print("Exact pattern not found. Trying normalized search...")
    # Normalize whitespace and try
    import re
    # Find the pattern more flexibly
    pattern = r'\},\s*["\']?collected_at["\']?:\s*["\']2026-04-12T10:54:00\+08:00["\']?\s*\},\s*\{'
    match = re.search(pattern, content)
    if match:
        print(f"Found pattern at {match.start()}: {repr(match.group()[:80])}")
        
        # Get the full matched text
        matched_text = match.group()
        
        # Build replacement
        new_content = content[:match.start()] + ',\n    {' + content[match.end():]
        
        # Also need to remove the old daily_summary that's before this collected_at
        # Let's check if there's a daily_summary before this point
        
        try:
            data = json.loads(new_content)
            print(f"\n*** JSON FIXED! ***")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved! Hours: {len(data['hourly_records'])}")
        except Exception as e2:
            print(f"Still error: {e2}")
