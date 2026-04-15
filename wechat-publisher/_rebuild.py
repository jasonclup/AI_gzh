import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} chars")

# Find all hour positions
hours = list(re.finditer(r'"hour": "(\d{2})"', content))
print(f"Found {len(hours)} hour entries:")
for h in hours:
    print(f"  Hour {h.group(1)} at position {h.start()}")

# Extract each hourly_record as a JSON object by finding balanced braces
# Simple approach: find start of each hour record and end (next hour or end)

records = []
for i, h in enumerate(hours):
    hour_val = h.group(1)
    start = content.rfind('{', 0, h.start())  # Find the { that opens this record
    
    # Find the end of this record - it's before the next record's { or at end/summary
    if i < len(hours) - 1:
        next_start = hours[i+1].start()
        # Go back to find }, that closes this record
        end = content.rfind('}\n', start, next_start) + 1
    else:
        # Last record - find before daily_summary or EOF
        end = len(content)
    
    # Actually let me try a different approach: just extract from { to matching }
    # For now, let's use positions
    
    print(f"  Hour {hour_val}: record around {start}-{end}")

# SIMPLER APPROACH: Just rebuild the whole file properly
# We know all the data is there, just the structure is broken at one point

# Find where the break is - after hour 10 data, there's extra stuff
h10_end_area = content[hours[2].start():hours[3].start()]
print(f"\nBetween hour 10 and 11 ({len(h10_end_area)} chars):")
# Show first and last 200 chars
if len(h10_end_area) > 400:
    print("FIRST:", repr(h10_end_area[:200]))
    print("LAST:", repr(h10_end_area[-200:]))
else:
    print(repr(h10_end_area))
