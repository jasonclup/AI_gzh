import json

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: Find the last hourly_records entry (hour 10) ending
# Then find where the new data (hour 11) starts
# Remove everything between them (old daily_summary + collected_at)

# Find "hour": "10" 
h10 = content.find('"hour": "10",')
print(f"Hour 10 at: {h10}")

# Find "hour": "11"
h11 = content.find('"hour": "11",')
print(f"Hour 11 at: {h11}")

# The problematic area is between hour 10's closing and hour 11
# Let's look at what's between them
between = content[h11-200:h11]
print(f"Before hour 11:\n{repr(between)}")

# Find the pattern: old data ends with }, then old daily_summary/collected_at }
# Then new data starts with }, { "hour": "11"

# Let's try a different approach: split by hourly_records entries
# and reconstruct

# Find all hour markers
import re
hours_pos = [(m.start(), m.group()) for m in re.finditer(r'"hour": "\d{2}"', content)]
print(f"\nFound {len(hours_pos)} hour markers:")
for pos, h in hours_pos:
    print(f"  {h} at position {pos}")
