# Fix line 132: add missing double quote after summary:
with open('_run_round_v2.py', 'rb') as f:
    lines = f.readlines()

line = lines[131]  # line 132

# The problem is: "summary:" should be "summary":" but the opening " after : is missing
# Find "summary:" and replace with "summary":"
old = b'"summary:"'
new = b'"summary":"'

if old in line:
    line = line.replace(old, new, 1)
    print('Fixed! Added missing quote after summary:')
    # Verify
    idx = line.find(b'summary')
    print(repr(line[idx:idx+30]))
else:
    print('Pattern not found, checking...')
    idx = line.find(b'summary')
    print(repr(line[idx:idx+25]))

lines[131] = line
with open('_run_round_v2.py', 'wb') as f:
    f.writelines(lines)
