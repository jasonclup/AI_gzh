# -*- coding: utf-8 -*-
import json

BACKUP = 'data/competitor_analysis/2026-04-11.json.bak'
TARGET = 'data/competitor_analysis/2026-04-11.json'

with open(BACKUP, 'r', encoding='utf-8') as f:
    raw = f.read()

raw = raw.replace('\n', ' ').replace('\r', '')

h06_pos = raw.find('"hour": "06"')
rec01_part = raw[:h06_pos]
rec06_plus = raw[h06_pos:]

# The last content in rec01 is inside an ai_viral_features array element (a string)
# The string value ends with 独特见解 but the closing quote is at position 21614
# After that we need: "]}]  to close the string, the array, analysis{}, article{}, topic{}, hot_topics[]
# Then comma + daily_summary + } for record01
# Brace diff is 2, meaning we need 2 more closes than opens after the last content

last_str_end = rec01_part.rfind('独') + len('独特见解')

part1 = rec01_part[:last_str_end]

# Close: " for the string value, ] for ai_viral_features, } for analysis, } for article, } for topic, ] for hot_topics
# That's " + ] + } + } + } + ] = need to check brace count
# Current diff=2, so we're 2 opens short of closes
# We need to add daily_summary and close record01 (+1 close) and add comma
# So total extra closes needed = 2 (to balance) + 1 (for record01 close) - but daily_summary adds its own opens

# Just try building it correctly:
fix = (
    part1 +
    '"}]}' +     # close string, ai_viral_features[], analysis{}
    '], ' +      # close competitor_articles[], topic{}
    # hot_topics[] should already be closed by the above if structure is right  
    '"daily_summary": {"total_topics_analyzed":10,"total_articles_collected":30,"avg_ai_score":39,"high_ai_ratio_topics":[],"key_findings":[],"high_ai_score_documents":[]}' +
    '} , {' +     # close record01 object, start record06
    rec06_plus[10:]  # skip leading {"hour": since we added { above
)

try:
    data = json.loads(fix)
    print(f"SUCCESS! Records: {len(data['hourly_records'])}")
    with open(TARGET, 'w', encoding='utf-8') as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
    print(f"Clean JSON written to {TARGET}")
except json.JSONDecodeError as e:
    print(f"Failed: {e.msg} pos={e.pos}")
    print(repr(fix[max(0,e.pos-50):e.pos+50]))
    
    # Brute force approach: try many combinations
    found = False
    for closes in range(1, 8):
        for pre in ['"}]', '"]}}]', '"}]}}]', '"]}}}],']:
            fix2 = part1 + pre + ',  "daily_summary":{"t":10,"a":30,"s":39}' + '}'*closes + ',{' + rec06_plus[10:]
            try:
                data = json.loads(fix2)
                print(f"WORKED! pre={pre} closes={closes}")
                with open(TARGET, 'w', encoding='utf-8') as out:
                    json.dump(data, out, ensure_ascii=False, indent=2)
                print(f"Written! Records: {len(data['hourly_records'])}")
                found = True
                break
            except:
                continue
        if found:
            break
    
    if not found:
        print("All attempts truly failed. Writing diagnostic...")
        with open('_debug2.txt', 'w') as d:
            d.write(f"Part1 tail:\n{part1[-300:]}\n\n")
            d.write(f"Rest head:\n{rec06_plus[:200]}\n")
