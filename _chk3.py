# -*- coding: utf-8 -*-
import json
path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where brace mismatch starts - walk through tracking depth
depth = 0
pos = 0
in_string = False
escape_next = False
for i, ch in enumerate(content):
    if escape_next:
        escape_next = False
        continue
    if ch == '\\' and in_string:
        escape_next = True
        continue
    if ch == '"' and not escape_next:
        in_string = not in_string
        continue
    if in_string:
        continue
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth < 0:
            print(f"Extra }} at pos {i}")
            break

print(f"Final depth at end: {depth}")
if depth > 0:
    print(f"Missing {depth} closing brace(s)")
    # Show context around where depth was last incremented without matching
    # Walk again and note when depth goes above expected
