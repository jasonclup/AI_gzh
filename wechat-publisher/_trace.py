# -*- coding: utf-8 -*-
import json

BACKUP = 'data/competitor_analysis/2026-04-11.json.bak'
TARGET = 'data/competitor_analysis/2026-04-11.json'

with open(BACKUP, 'r', encoding='utf-8') as f:
    raw = f.read()

raw = raw.replace('\n', ' ').replace('\r', '')

# The data at pos 21619 onwards looks fine: "}]}], "daily_summary"
# But JSON parser says "Expecting ',' delimiter" at pos 21619
# This means at pos 21619 it found } but expected , or }
# This happens when inside an array/object and the parser thinks we need another element

# The brace diff of 2 means we have 2 more { than } before pos 21619
# So when we hit }}] at 21619-21, those closes bring us to diff=0 for braces 
# BUT the structure might be wrong - maybe an array wasn't properly started with [

# Let me check bracket balance too
prefix = raw[:21619]
opens_b = prefix.count('[')
closes_b = prefix.count(']')
print(f"Brackets up to 21619: [={opens_b} ]={closes_b} diff={opens_b-closes_b}")
o = prefix.count('{'); c = prefix.count('}'); print(f"Braces up to 21619: open={o} close={c}")


# Theory: there's an extra { without matching } BEFORE pos 21619
# OR there's a missing [ somewhere
# The error "Expecting ',' delimiter" at } position means:
# We're inside an object or array, parser sees }, 
# but the current context expects either a value (after :) or another key-value pair (after ,)

# Let me trace: after the string value ending at 218("), 
# pos 219 is } which closes something
# If parser thinks we're inside ai_viral_features ARRAY, then } is unexpected (should be , or ])
# If parser thinks we're inside analysis OBJECT, then } might close it but then need , or ]

# Most likely: one of the parent arrays/objects was already closed, 
# so these extra }}] are closing too many levels

# SOLUTION: just remove 2 opening braces from somewhere early in record 01,
# or add proper structure. 

# Actually simplest fix: since records 06 and 07 are intact, 
# let's just write a clean file with only 06, 07 data + our new 08 data
h06 = raw.find('"hour": "06"')
h07 = raw.find('"hour": "07"')

rec06_raw = raw[h06:h07]
rec07_raw = raw[h07:]

# Try wrapping each as standalone JSON
for label, rdata, start_marker in [("06", rec06_raw, h06), ("07", rec07_raw, h07)]:
    # Build a minimal wrapper
    test_json = '{"a":[{' + rdata[10:] + '}]}'
    try:
        j = json.loads(test_json)
        print(f"Record {label}: OK!")
    except json.JSONDecodeError as e:
        # Find the first error position within this record  
        print(f"Record {label}: ERROR at relative pos {e.pos}")
        rel_pos = e.pos
        if rel_pos > 10:
            ctx = rdata[max(0,rel_pos-30):rel_pos+30]
            print(f"  Context: {repr(ctx)}")

# New approach: just build from scratch using our hour 08 script
# Write only 06 and 07 data by extracting more carefully
