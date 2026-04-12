# -*- coding: utf-8 -*-
"""Fix summary fields in hourly_08 gen script"""
with open('_gen_hourly_08.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Fix lines with problematic summary pattern: "summary": " "...",
    if '"summary":' in line and line.strip().startswith('"summary"'):
        # Check if this line has a nested quote issue (Chinese quote inside)
        # Replace the broken pattern
        pass
    fixed_lines.append(line)

# Actually let's just do a simple replace for the specific broken pattern
text = ''.join(lines)
# The problem is: "summary": "  "actual content"
# Need to remove extra space+quote after summary":
import re
text = re.sub(r'"summary":\s+"(\s*")', r'"summary": "', text)

with open('_gen_hourly_08.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done fixing")
