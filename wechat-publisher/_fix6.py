# Fix ALL occurrences of missing quote after summary:
with open('_run_round_v2.py', 'rb') as f:
    raw = f.read()

# Fix pattern: "summary:"value -> "summary":"value
import re
count = 0
def replacer(m):
    global count
    count += 1
    return b'"summary":"'

raw, n = re.subn(b'"summary:"', replacer, raw)
print(f'Fixed {n} occurrences of missing summary quote')

with open('_run_round_v2.py', 'wb') as f:
    f.write(raw)

print('Done')
