import os, hashlib
d = r'C:\Users\v_junshshi\WorkBuddy\Claw\wechat-publisher\output\images'
files = sorted([f for f in os.listdir(d) if f.startswith(('GPT', 'Industry', 'AI_GPT', 'Future'))])
print(f'Generated {len(files)} images:')
for f in files:
    p = os.path.join(d, f)
    sz = os.path.getsize(p)
    md5 = hashlib.md5(open(p, 'rb').read()).hexdigest()[:12]
    print(f'  {sz//1024}KB | md5={md5} | {f}')
md5s = set(hashlib.md5(open(os.path.join(d, f), 'rb').read()).hexdigest()[:12] for f in files)
result = 'ALL DIFFERENT!' if len(md5s) == len(files) else 'SOME DUPLICATES'
print(f'\nUnique: {len(md5s)}/{len(files)} => {result}')
