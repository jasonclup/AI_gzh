import json, glob, os

# 查最新文章数据
js = glob.glob('output/flow_result.json')
if js:
    with open(js[0], 'r', encoding='utf-8') as f:
        data = json.load(f)
    article = data.get('article', {})
    
    print('=== 文章标题 ===')
    print(article.get('title', 'N/A'))
    print()
    print(f'总字数: {article.get("word_count", "N/A")}')
    print()
    
    print('=== 各段信息 ===')
    for i, sec in enumerate(article.get('sections', [])):
        ptype = sec.get('type', '?')
        text = (sec.get('text', '') or '')[:80]
        img = sec.get('image_path', '')
        prompt = (sec.get('image_prompt', '') or '')[:100]
        print(f'--- [{i}] type={ptype} ---')
        print(f'  text: {text}...')
        print(f'  image_path: {img}')
        if prompt:
            print(f'  prompt: {prompt}...')
        else:
            print(f'  prompt: 无!')
        print()
