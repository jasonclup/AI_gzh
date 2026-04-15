# -*- coding: utf-8 -*-
import json
path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
try:
    data = json.loads(content)
    print("OK! Roles:", list(data['personalities'].keys()))
except json.JSONDecodeError as e:
    print(f"Error pos={e.pos}")
    start = max(0, e.pos - 60)
    end = min(len(content), e.pos + 60)
    with open(r'_json_err.txt', 'w', encoding='utf-8') as f:
        f.write(f"pos={e.pos}\n")
        f.write(repr(content[start:end]) + '\n')
        # also show line info  
        lines = content[:e.pos].count('\n') + 1
        f.write(f"line={lines}\n")
        f.write(f"\nLast 200:\n{repr(content[-200:])}")
    print("Written to _json_err.txt")
