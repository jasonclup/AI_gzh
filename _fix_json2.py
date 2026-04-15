# -*- coding: utf-8 -*-
"""Fix all Python expression strings in personalities.json - round 2"""
import json, re

path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

replacements = []

# Fix "string" + "string" concatenation inside template values
# Pattern: "...", "...." + "....\n..." 
# This is tricky because + is also in URLs. Look for: "ends with quote" space "+" space "starts
def fix_concat(m):
    expr = m.group(0)
    replacements.append(f"concat: {expr[:100]}")
    # Join the string parts (strip quotes and +)
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', expr)
    if len(parts) >= 2:
        joined = ''.join(parts)
        return '"' + joined + '"'
    return expr

# Match patterns like: "text" + "\nmore text"
content = re.sub(r'"[^"]*"\s*\+\s*"[^"]*"', fix_concat, content)

# Also fix any remaining ternary
def fix_ternary(m):
    expr = m.group(0)
    replacements.append(f"ternary2: {expr[:80]}")
    parts = expr.split(' if ')
    if len(parts) >= 2:
        return parts[0].rstrip()
    return expr

content = re.sub(r'"([^"]*?)\s+if\s+[^"]+\s+else\s+[^"]*"', fix_ternary, content)

with open(r'_fix_log2.txt', 'w', encoding='utf-8') as lf:
    for r in replacements:
        lf.write(f"  {r}\n")

try:
    data = json.loads(content)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(r'_fix_log2.txt', 'a', encoding='utf-8') as lf:
        lf.write("\nSUCCESS!\n")
        lf.write(f"Roles: {list(data.get('personalities', {}).keys())}\n")
except json.JSONDecodeError as e:
    with open(r'_fix_log2.txt', 'a', encoding='utf-8') as lf:
        lf.write(f"\nBROKEN at pos {e.pos}:\n")
        snippet = content[max(0,e.pos-60):e.pos+60]
        lf.write(repr(snippet) + '\n')
