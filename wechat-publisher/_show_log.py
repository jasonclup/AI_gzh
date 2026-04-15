import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('_v3_run.log', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 只打印关键行（跳过 CLIXML 噪声）
for l in lines[-80:]:
    s = l.strip()
    if not s or s.startswith('<Objs') or s.startswith('</Objs') or s.startswith('<') and 'CLIXML' in s:
        continue
    print(l, end='')
