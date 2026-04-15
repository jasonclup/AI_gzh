import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find old ending
old_marker = '"collected_at": "2026-04-12T10:54:00+08:00"\n}'

if old_marker in content:
    idx = content.find(old_marker)
    print(f"Found old marker at position {idx}")
    
    # Find old daily_summary start (search backwards from idx)
    ds_start = content.rfind('\n  "daily_summary"', 0, idx)
    print(f"Old daily_summary starts at {ds_start}")
    
    # Content before old daily_summary
    before = content[:ds_start]
    
    # Content after the old closing }
    after = content[idx+len(old_marker):].lstrip()
    print(f"After old marker: {repr(after[:80])}")
    
    # after starts with },\n    { "hour": "11", ...
    # Remove the leading },\n since we're continuing hourly_records array
    if after.startswith('},'):
        # Find the newline after },
        nl_pos = after.find('\n')
        if nl_pos > 0:
            after = after[nl_pos+1:].lstrip()
            print(f"After trimming: {repr(after[:80])}")
    
    new_content = before + '\n' + after
    
    try:
        data = json.loads(new_content)
        hours = len(data['hourly_records'])
        topics = data['daily_summary']['total_topics']
        articles = data['daily_summary']['total_articles']
        print(f"JSON VALID! Hours={hours}, Topics={topics}, Articles={articles}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        size = len(json.dumps(data, ensure_ascii=False)) / 1024
        print(f"Saved! File size: {size:.1f} KB")
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\_debug_fix.json', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Debug output written")
else:
    print("Old marker not found!")
