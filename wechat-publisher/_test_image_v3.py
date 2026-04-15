# -*- coding: utf-8 -*-
"""测试配图v3模块"""
import json, sys
sys.path.insert(0, '.')
from modules.image_generator_v3 import ImageGenModuleV3

gen = ImageGenModuleV3({'OUTPUT_DIR': './output'})

print('=' * 60)
print('[Image Plan v3] Test 1: Real Product Topic')
print('=' * 60)

plan = gen.analyze_topic_for_images(
    topic='姚安娜代言华为新手机Pura X Max',
    title='姚安娜代言华为这事儿，我看完只说一句',
    article_text='华为选代言人从来不为了带货，这次请姚安娜代言Pura X Max折叠屏手机，背后是品牌自信的体现。'
)

cover = plan['cover']
print(f'\n[COVER] Type: {cover["type"]}')
if cover['type'] == 'real':
    print(f'  Search Query: {cover["search_query"]}')
else:
    print(f'  AI Prompt: {cover["ai_prompt"][:80]}...')
print(f'  Reason: {cover["reason"]}')

print(f'\n[PARA IMAGES] Count: {len(plan["paragraphs"])}')
for p in plan['paragraphs']:
    label = f'Para {p["position"]}'
    if p['type'] == 'real':
        print(f'  {label}: REAL -> search: {p["search_query"]}')
    else:
        prompt = p.get('ai_prompt', '')
        print(f'  {label}: AI -> {prompt[:70]}...')

products = [r['match'] for r in plan['real_products_found']]
print(f'\n[REAL PRODUCTS DETECTED]: {products}')

# Test 2: No real product
print('\n' + '=' * 60)
print('[Image Plan v3] Test 2: Abstract/Policy Topic')
print('=' * 60)

plan2 = gen.analyze_topic_for_images(
    topic='交管部门回应新能源车牌绿色变白色',
    title='新能源？别急，先看完这篇再下结论',
)

cover2 = plan2['cover']
print(f'\n[COVER] Type: {cover2["type"]}')
if cover2['type'] == 'real':
    print(f'  Search: {cover2["search_query"]}')
else:
    print(f'  AI: {cover2["ai_prompt"][:80]}...')
print(f'  Reason: {cover2["reason"]}')

print(f'\n[PARA IMAGES] Count: {len(plan2["paragraphs"])}')
for p in plan2['paragraphs']:
    label = f'Para {p["position"]}'
    if p['type'] == 'real':
        print(f'  {label}: REAL -> {p["search_query"]}')
    else:
        prompt = p.get('ai_prompt', '')
        print(f'  {label}: AI -> {prompt[:70]}...')

products2 = [r['match'] for r in plan2['real_products_found']]
print(f'\n[REAL PRODUCTS DETECTED]: {products2 if products2 else "(none - all AI images)"}')
