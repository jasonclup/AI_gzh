# -*- coding: utf-8 -*-
import json, re

path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File length: {len(content)}")

try:
    data = json.loads(content)
    print("JSON OK!")
except json.JSONDecodeError as e:
    print(f"Error at pos {e.pos}, line {e.lineno}")
    # Show surrounding context
    start = max(0, e.pos - 80)
    end = min(len(content), e.pos + 80)
    snippet = content[start:end]
    with open(r'_error_ctx.txt', 'w', encoding='utf-8') as f:
        f.write(f"Pos: {e.pos}\n")
        f.write(f"Snippet:\n{repr(snippet)}\n\n")
        # Show last 500 chars
        f.write(f"\nLast 500 chars:\n{repr(content[-500:])}")
    print(f"Written to _error_ctx.txt")
