# -*- coding: utf-8 -*-
"""Final fix: all Python expressions in personalities.json via raw string replacement"""
import re, json

path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

log = []

# ---- Fix 1: "char" * N patterns ----
def fix_mul_expr(m):
    expr = m.group(0)
    log.append(f"MUL: {expr[:60]}")
    inner = re.search(r'"(.)"\s*\*\s*(\d+)', expr)
    if inner:
        return '"' + inner.group(1) * int(inner.group(2)) + '"'
    return expr

content = re.sub(r'"[^"]{1,3}"\s*\*\s*\d+', fix_mul_expr, content)

# ---- Fix 2: "str" + "str" concat ----
def fix_concat_expr(m):
    expr = m.group(0)
    log.append(f"CONCAT: {expr[:80]}")
    parts = re.findall(r'"((?:[^"\\]|\\.)*)"', expr)
    if len(parts) >= 2:
        return '"' + ''.join(parts) + '"'
    return expr

# Keep replacing until no more concatenation found
for _ in range(10):
    new_content = re.sub(r'"[^"]*"\s*\+\s*"[^"]*"', fix_concat_expr, content)
    if new_content == content:
        break
    content = new_content

# ---- Fix 3: ternary in templates {x ? 'a' : 'b'} or "x if cond else y" ----
def fix_ternary_template(m):
    """Fix ternary inside template like {has_issue ? 'a' : 'b'}"""
    expr = m.group(0)
    log.append(f"TERNARY_TPL: {expr[:80]}")
    # Replace with just the true branch value
    # Pattern: {var ? 'value1' : 'value2'} -> {'value1'}
    inner = re.search(r"\{([^?]*)\s*\?\s*'([^']*)'\s*:\s*'([^']*)'\}", expr)
    if inner:
        return "'" + inner.group(2) + "'"
    return expr

content = re.sub(r"\{[^{}]*\?[^{}]*:[^{}]*\}", fix_ternary_template, content)

# Also fix "val if cond else other" style
def fix_ternary_str(m):
    expr = m.group(0)
    log.append(f"TERNARY_STR: {expr[:80]}")
    parts = expr.split(' if ')
    if len(parts) >= 2:
        return parts[0].rstrip().rstrip('"') + '"'
    return expr

content = re.sub(r'"([^"]*?)\s+if\s+[^"]+\s+else\s+[^"]*"', fix_ternary_str, content)

# Write log
with open(r'_fix_final_log.txt', 'w', encoding='utf-8') as lf:
    for l in log:
        lf.write(l + '\n')

# Validate
try:
    data = json.loads(content)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(r'_fix_final_log.txt', 'a', encoding='utf-8') as lf:
        lf.write('\n=== SUCCESS! File saved. ===\n')
        lf.write(f"Roles: {list(data['personalities'].keys())}\n")
    print("OK!")
except json.JSONDecodeError as e:
    with open(r'_fix_final_log.txt', 'a', encoding='utf-8') as lf:
        lf.write(f'\nFAILED at pos {e.pos}:\n')
        lf.write(repr(content[max(0,e.pos-60):e.pos+60]) + '\n')
        lf.write(f'\nLast 300 chars:\n{repr(content[-300:])}\n')
    print(f"Still broken at pos {e.pos}")
