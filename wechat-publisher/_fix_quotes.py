# Fix quote issues in _run_round_15.py - brute force approach
with open('_run_round_15.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Line 535 has: "publish_time': '2026...'  (mixed quotes!)
# Strategy: find all lines containing ': ' (colon+space+single quote) and fix them

import re

lines = content.split('\n')
fixed = []
for idx, line in enumerate(lines):
    # Pattern: key": 'value' or key': 'value' - mixed quotes
    # Fix: replace single-quote-wrapped values with double-quote-wrapped values
    if re.search(r': \'[^\']*\',?\s*$', line) or re.search(r'^\s+\'.+\':\s*\'', line):
        line = line.replace("'", '"')
    fixed.append(line)

with open('_run_round_15.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed))

print('Fixed. Verifying...')
exec(compile(open('_run_round_15.py', 'r', encoding='utf-8').read(), '_run_round_15.py', 'exec'))
print('Syntax OK, running script now...')
