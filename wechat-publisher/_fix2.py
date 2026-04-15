# Fix Chinese curly quotes in _run_round_v2.py
with open('_run_round_v2.py', 'r', encoding='utf-8') as f:
    c = f.read()

lines = c.split('\n')
out = []
for line in lines:
    if '\u201c' in line or '\u201d' in line:
        line = line.replace('\u201c', '\u300a').replace('\u201d', '\u300b')
    out.append(line)

with open('_run_round_v2.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print('Fixed Chinese quotes in _run_round_v2.py')
