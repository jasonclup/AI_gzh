import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find exact bytes around the problem area
target = '"collected_at": "2026-04-12T10:54:00+08:00"'
idx = content.find(target)
print(f"Found at idx={idx}")
print(f"Context:\n{repr(content[idx-30:idx+len(target)+30])}")

# Get 200 chars around the old daily_summary
ds_idx = content.find('"daily_summary"')
# Find the last daily_summary (there are two - old and new)
last_ds = content.rfind('"daily_summary"', 0, idx + len(target))
print(f"\nLast daily_summary before collected_at: {last_ds}")
print(f"Context:\n{repr(content[last_ds:last_ds+200])}")

# The fix: take everything up to (but not including) the old daily_summary
# Then add the new data starting from hour 11

# Actually let's just find the old daily_summary section boundaries
old_ds_start = content.find('  "daily_summary": {', content.find('"hour": "10"'))
print(f"\nOld daily_summary starts at: {old_ds_start}")

# Find what comes after the old } that closes the whole object
# It should be },\n    { "hour": "11"
search_from = content.find(target) + len(target)

print(f"\nSearching from {search_from}:")
print(repr(content[search_from:search_from+50]))

# Build new content: everything before old daily_summary + from hour 11 onwards
before = content[:old_ds_start]

# Find hour 11 start
h11_start = content.find('"hour": "11"')
# Go back to find the { or },
before_h11 = content.rfind('},', 0, h11_start)
# Actually we need to find where the array continuation starts
# After old collected_at there's }\n,\n    {
after_old = content[search_from:]
print(f"\nafter_old starts with: {repr(after_old[:50])}")

# after_old should be \n}\n,\n    {\n      "hour": "11"
# We want to skip the \n} part and keep ,\n    {

if after_old.strip().startswith('}'):
    # Find the comma after }
    comma_pos = after_old.find(',')
    if comma_pos > 0:
        after = after_old[comma_pos:]  # Start from the comma
        new_content = before.rstrip() + '\n' + after.lstrip()
        
        try:
            data = json.loads(new_content)
            print(f"\nJSON VALID! Hours: {len(data['hourly_records'])}")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved! Size: {len(json.dumps(data, ensure_ascii=False))/1024:.1f} KB")
        except json.JSONDecodeError as e:
            print(f"\nStill error: {e}")
            # Write debug
            with open(r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\_debug.json', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Debug written to _debug.json")
