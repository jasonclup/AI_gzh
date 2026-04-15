# -*- coding: utf-8 -*-
import json
path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Walk tracking depth, report position when depth first becomes wrong
depth = 0
in_string = False
escape_next = False
last_positions = {}  # depth -> pos of the { that got us here

for i, ch in enumerate(content):
    if escape_next:
        escape_next = False
        continue
    if ch == '\\' and in_string:
        escape_next = True
        continue
    if ch == '"' and not escape_next:
        in_string = not in_string
        continue
    if in_string:
        continue
    if ch == '{':
        depth += 1
        last_positions[depth] = i
    elif ch == '}':
        depth -= 1

print(f"End depth: {depth}")
if depth > 0:
    # The extra { is at last_positions[final_depth]
    # Actually we need to find which { was never closed
    # Show all positions where { pushed to current final depth or beyond
    print(f"Last unclosed {{ at pos: {last_positions.get(depth+1, 'unknown')}")
    
    # Show context around that area
    for d, p in sorted(last_positions.items()):
        if d >= depth:  # these are the ones that may not be closed
            start = max(0, p - 40)
            end = min(len(content), p + 60)
            snippet = content[start:end]
            with open(r'_brace_info.txt', 'a', encoding='utf-8') as f:
                f.write(f"\nDepth={d}, pos={p}:\n{repr(snippet)}\n")
    
    print("Details written to _brace_info.txt")
