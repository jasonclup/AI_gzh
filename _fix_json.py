# -*- coding: utf-8 -*-
"""Fix all Python expression strings in personalities.json"""
import json, re

path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements_made = []

# Fix all "X" * N patterns
def fix_mul(m):
    expr = m.group(0)
    replacements_made.append(expr[:60])
    # Extract the char and count
    inner = re.search(r'"(.)"\s*\*\s*(\d+)', expr)
    if inner:
        ch, n = inner.group(1), int(inner.group(2))
        return '"' + ch * n + '"'
    return expr

content = re.sub(r'"[^"]{1,3}"\s*\*\s*\d+', fix_mul, content)

# Fix ternary: "x if cond else y" - replace with just x (the true branch)
def fix_ternary(m):
    expr = m.group(0)
    replacements_made.append(f"ternary: {expr[:80]}")
    # Take only the part before 'if'
    parts = expr.split(' if ')
    if len(parts) >= 2:
        return parts[0].rstrip()
    return expr

content = re.sub(r'"([^"]*?)\s+if\s+[^"]+\s+else\s+[^"]*"', fix_ternary, content)

# Write to log
with open(r'_fix_log.txt', 'w', encoding='utf-8') as lf:
    lf.write(f"Replacements made:\n")
    for r in replacements_made:
        lf.write(f"  {r}\n")

# Try parse
try:
    data = json.loads(content)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(r'_fix_log.txt', 'a', encoding='utf-8') as lf:
        lf.write(f"\nSUCCESS! Roles: {list(data.get('personalities', {}).keys())}\n")
except json.JSONDecodeError as e:
    with open(r'_fix_log.txt', 'a', encoding='utf-8') as lf:
        lf.write(f"\nSTILL BROKEN at pos {e.pos}:\n")
        snippet = content[max(0,e.pos-50):e.pos+50]
        lf.write(repr(snippet) + '\n')
