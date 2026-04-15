# -*- coding: utf-8 -*-
import re
"""Final fix for remaining expression in developer template"""
path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

log = []

# Fix 1: Remaining {var ? 'a' + x : 'b'} pattern
def fix_complex_ternary(m):
    expr = m.group(0)
    log.append(f"COMPLEX_TERNARY: {expr[:100]}")
    # Just use the true branch value without the concat part
    return "'需要关注的技术问题'"

content = re.sub(r"\{has_issue\s*\?[^}]+\}", fix_complex_ternary, content)

# Write
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'_fix_final2_log.txt', 'w', encoding='utf-8') as lf:
    for l in log:
        lf.write(l + '\n')

import json
try:
    data = json.loads(content)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(r'_fix_final2_log.txt', 'a', encoding='utf-8') as lf:
        lf.write('\n=== SUCCESS! ===\n')
        lf.write(f"Roles: {list(data['personalities'].keys())}\n")
    print("OK!")
except json.JSONDecodeError as e:
    with open(r'_fix_final2_log.txt', 'a', encoding='utf-8') as lf:
        lf.write(f'\nFAILED at pos {e.pos}:\n')
        lf.write(repr(content[max(0,e.pos-60):e.pos+60]) + '\n')
        # Show full tail
        lf.write(f'\nTail:\n{repr(content[-400:])}\n')
    print(f"Broken at {e.pos}")
