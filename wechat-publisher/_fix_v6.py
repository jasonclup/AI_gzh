# -*- coding: utf-8 -*-
"""Replace _build_anti_ai_prompt with v6 tech-gossip version"""
import os

f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules', 'article_generator.py')
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

s = c.find('        # 根据风格选择语气')
e = c.find('\n        return prompt', s)
print(f'Found: start={s} end={e}')

if s < 0 or e < 0:
    print('ERROR: markers not found!')
    exit(1)

# Read the new prompt from a separate file to avoid all quoting issues
new_prompt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_v6_prompt_body.txt')
with open(new_prompt_file, 'r', encoding='utf-8') as nf:
    new_code = nf.read()

c = c[:s] + new_code + c[e:]
with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print(f'SUCCESS! Updated {f}. Size: {len(c)} bytes')
