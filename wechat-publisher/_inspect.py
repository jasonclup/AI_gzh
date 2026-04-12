# -*- coding: utf-8 -*-
import json

BACKUP = 'data/competitor_analysis/2026-04-11.json.bak'
TARGET = 'data/competitor_analysis/2026-04-11.json'

with open(BACKUP, 'r', encoding='utf-8') as f:
    raw = f.read()

raw = raw.replace('\n', ' ').replace('\r', '')

# Error is ALWAYS at position 21619
# Let's see EXACTLY what's there byte by byte around 21617-21625
for i in range(21610, 21635):
    c = raw[i]
    print(f"  pos {i}: U+{ord(c):04X} {repr(c)}")

print("\n--- The full context ---")
ctx = raw[21580:21660]
print(repr(ctx))
