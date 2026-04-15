# Fix Chinese curly quotes - brute force byte-level approach
with open('_run_round_v2.py', 'rb') as f:
    raw = f.read()

# Replace the problematic Unicode characters
raw = raw.replace(b'\xe2\x80\x9c', b'\xe3\x80\x8a')  # " (U+201C) -> \u300a (
raw = raw.replace(b'\xe2\x80\x9d', b'\xe3\x80\x8b')  # " (U+201D) -> \u300b )

with open('_run_round_v2.py', 'wb') as f:
    f.write(raw)

print('Fixed at byte level')
