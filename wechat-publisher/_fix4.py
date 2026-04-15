# Fix fullwidth colon (U+FF1A = ef bc 9a) that breaks Python strings
with open('_run_round_v2.py', 'rb') as f:
    raw = f.read()

# Replace fullwidth colon (：) with regular colon (:)
raw = raw.replace(b'\xef\xbc\x9a', b':')

with open('_run_round_v2.py', 'wb') as f:
    f.write(raw)

print('Fixed fullwidth colons')
