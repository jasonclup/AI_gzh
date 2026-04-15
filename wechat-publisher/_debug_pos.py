import json, re

filepath = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\data\competitor_analysis\2026-04-12.json'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find ALL positions of key markers
print("=== MARKER ANALYSIS ===")
for m in re.finditer(r'"collected_at":\s*"([^"]+)"', content):
    print(f"  collected_at={m.group(1)} at pos {m.start()}")

for m in re.finditer(r'"daily_summary"', content):
    print(f"  daily_summary at pos {m.start()}")

# The second daily_summary (around pos 79027) is the old one that's problematic
# The first collected_at (pos ~81) is in the root object header area
# The second (pos ~50640) is inside hour 10 record  
# The third should be after old daily_summary - the problematic top-level one

# Let me look at what's around position 79000-85000
area = content[78900:85000]
print(f"\n=== AREA 78900-85000 ===")
print(area[:3000])
