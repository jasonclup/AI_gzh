# Fix Chinese quotes in _run_round_v2.py
with open('_run_round_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Chinese curly quotes (which break Python strings) with escaped versions or regular quotes
# The issue is "" inside double-quoted strings
content = content.replace('\u201c', '\\u201c')  # left double quotation mark
content = content.replace('\u201d', '\\u201d')  # right double quotation mark

with open('_run_round_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed Chinese quotes')
