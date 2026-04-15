# -*- coding: utf-8 -*-
import re

path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Show context around 9478
pos = 9478
with open(r'_context.txt', 'w', encoding='utf-8') as f:
    # Show char by char around the position
    start = max(0, pos - 100)
    end = min(len(content), pos + 100)
    snippet = content[start:end]
    f.write(f"Context around pos {pos}:\n")
    f.write(f"Position {pos} char: {repr(content[pos])}\n")
    f.write(f"\nSnippet:\n{repr(snippet)}\n")
    
# Also check: is there a duplicate key or unclosed brace?
# Count braces
open_braces = content.count('{')
close_braces = content.count('}')
open_brackets = content.count('[')
close_brackets = content.count(']')
with open(r'_context.txt', 'a', encoding='utf-8') as f:
    f.write(f"\n{{ : {open_braces} vs }} : {close_braces}\n")
    f.write(f"[ : {open_brackets} vs ] : {close_brackets}\n")
    
# Find where interaction_rules starts
idx = content.find('interaction_rules')
if idx >= 0:
    with open(r'_context.txt', 'a', encoding='utf-8') as f:
        f.write(f"\ninteraction_rules found at pos {idx}\n")
        f.write(content[idx:idx+200])
