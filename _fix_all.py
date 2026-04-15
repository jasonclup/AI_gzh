# -*- coding: utf-8 -*-
import re, json
"""
Read the current broken file, do ALL fixes in memory,
then validate before writing.
"""
path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

content = raw
fixes = []

# Fix 1: "X" * N  => repeat char N times
for m in re.finditer(r'"(.)"\s*\*\s*(\d+)', content):
    ch, n = m.group(1), int(m.group(2))
    old = m.group(0)
    new = '"' + (ch * n) + '"'
    content = content.replace(old, new, 1)
    fixes.append(f"mul: {old} -> {new[:30]}...")

# Fix 2: "str" + "str" concat - iterative
for iteration in range(20):
    found = False
    for m in re.finditer(r'"[^"]*"\s*\+\s*"[^"]*"', content):
        expr = m.group(0)
        parts = re.findall(r'"((?:[^"\\]|\\.)*)"', expr)
        if len(parts) >= 2:
            new = '"' + ''.join(parts) + '"'
            content = content[:m.start()] + new + content[m.end():]
            fixes.append(f"concat iter{iteration}: ...")
            found = True
            break
    if not found:
        break

# Fix 3: ternary templates {var ? 'a' : 'b'}
for m in re.finditer(r'\{([^{}]+)\?([^{}]+):([^{}])+\}', content):
    expr = m.group(0)
    # Extract true branch
    tmatch = re.search(r"'([^']*)'", expr)
    if tmatch:
        new = "'" + tmatch.group(1) + "'"
        content = content[:m.start()] + new + content[m.end():]
        fixes.append(f"ternary_tpl: {expr[:60]}... -> {new}")

# Fix 4: "val if cond else other"
for m in re.finditer(r'"([^"]*?)\s+if\s+[^"]+\s+else\s+[^"]*"', content):
    expr = m.group(0)
    before_if = expr.split(' if ')[0].rstrip().rstrip('"')
    new = before_if + '"'
    content = content[:m.start()] + new + content[m.end():]
    fixes.append(f"ternary_str: {expr[:60]}... -> {new[:40]}...")

# Write debug log
with open(r'_all_fixes_log.txt', 'w', encoding='utf-8') as lf:
    for fx in fixes:
        lf.write(fx + '\n')
    lf.write(f'\nTotal fixes: {len(fixes)}\n')
    lf.write(f'Content length: {len(content)}\n')

# Validate
try:
    data = json.loads(content)
    roles = list(data.get('personalities', {}).keys())
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(r'_all_fixes_log.txt', 'a', encoding='utf-8') as lf:
        lf.write(f'\n*** SUCCESS ***\n')
        lf.write(f'Roles ({len(roles)}): {roles}\n')
    print("SUCCESS!")
except json.JSONDecodeError as e:
    with open(r'_all_fixes_log.txt', 'a', encoding='utf-8') as lf:
        lf.write(f'\n*** FAILED at pos {e.pos} ***\n')
        start = max(0, e.pos - 80)
        end = min(len(content), e.pos + 80)
        lf.write(repr(content[start:end]) + '\n\n')
        lf.write(repr(content[-500:]) + '\n')
    print(f"FAILED pos={e.pos}")
