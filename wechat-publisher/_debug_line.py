# Debug line 132 of _run_round_v2.py
with open('_run_round_v2.py', 'rb') as f:
    lines = f.readlines()

line = lines[131]  # line 132 (0-indexed)
idx = line.find(b'summary')

print('Line 132 from summary onward:')
chunk = line[idx:idx+250]
print(repr(chunk))
print()

# Count quotes in the whole line
dq = line.count(b'"')
sq = line.count(b"'")
print(f'Double quotes: {dq}')
print(f'Single quotes: {sq}')

# Find all double quote positions
pos = 0
quote_positions = []
while True:
    p = line.find(b'"', pos)
    if p < 0:
        break
    quote_positions.append(p)
    pos = p + 1

print(f'Quote positions: {quote_positions}')

# Show what's around each quote
for i, p in enumerate(quote_positions):
    start = max(0, p-10)
    end = min(len(line), p+10)
    context = line[start:end]
    print(f'  Quote #{i+1} at pos {p}: ...{repr(context)}...')
