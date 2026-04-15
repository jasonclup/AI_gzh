# -*- coding: utf-8 -*-
"""Fix personalities.json by doing string-level fixes BEFORE json parsing"""
import re

path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

log = []

# Fix 1: "═" * 30 -> 30 ═ chars
old_count = content.count('"═" * 30')
content = content.replace('"═" * 30', '"══════════════════════════════"')
log.append(f"Fix '═'*30: {old_count} replacements")

# Fix 2: "string1" + "string2" concatenation inside JSON string values
# This pattern appears within template arrays
def replace_concat(match):
    full = match.group(0)
    log.append(f"Fix concat: {full[:80]}...")
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', full)
    if len(parts) >= 2:
        return '"' + ''.join(parts) + '"'
    return full

content = re.sub(r'"[^"]*"\s*\+\s*"[^"]*"', replace_concat, content)

# Fix 3: ternary "val if cond else other" -> just val
def replace_ternary(match):
    full = match.group(0)
    log.append(f"Fix ternary: {full[:80]}...")
    before_if = full.split(' if ')[0].rstrip()
    return before_if

content = re.sub(r'"([^"]*?)\s+if\s+[^"]+\s+else\s+[^"]*"', replace_ternary, content)

# Write log
with open(r'_fix_log3.txt', 'w', encoding='utf-8') as lf:
    for l in log:
        lf.write(l + '\n')

# Try to validate
import json
try:
    data = json.loads(content)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(r'_fix_log3.txt', 'a', encoding='utf-8') as lf:
        lf.write(f'\nSUCCESS! File saved.\n')
        lf.write(f'Roles: {list(data["personalities"].keys())}\n')
except json.JSONDecodeError as e:
    with open(r'_fix_log3.txt', 'a', encoding='utf-8') as lf:
        lf.write(f'\nFAILED at pos {e.pos}:\n')
        lf.write(repr(content[max(0,e.pos-50):e.pos+50]) + '\n')
