# -*- coding: utf-8 -*-
import json
path = r'c:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\modules\personalities.json'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find interaction_rules position
idx = content.find('interaction_rules')
print(f"interaction_rules at: {idx}")

# Show 200 chars before it
start = max(0, idx - 200)
snippet = content[start:idx+30]
with open(r'_json_err2.txt', 'w', encoding='utf-8') as f:
    f.write(f"Before interaction_rules:\n")
    f.write(repr(snippet) + '\n')
    
# Also count braces/brackets before this point
before = content[:idx]
ob = before.count('{')
cb = before.count('}')
osq = before.count('[')
csq = before.count(']')
f = open(r'_json_err2.txt', 'a', encoding='utf-8')
f.write(f"\nBraces before ir: {ob} open, {cb} close (diff={ob-cb})\n")
f.write(f"Brackets before ir: {osq} open, {csq} close (diff={osq-csq})\n")

# Total counts
total_ob = content.count('{')
total_cb = content.count('}')
total_osq = content.count('[')
total_csq = content.count(']')
f.write("\nTotal: open_braces=" + str(total_ob) + " close=" + str(total_cb) + " open_sq=" + str(osq) + " close=" + str(csq) + "\n")

try:
    data = json.loads(content)
    f.write("\nPARSED OK!")
except json.JSONDecodeError as e:
    f.write(f"\nError at pos {e.pos}, line {e.lineno}, col {e.colno}\n")
    s2 = max(0, e.pos-80)
    f.write(repr(content[s2:e.pos+80]))
f.close()
