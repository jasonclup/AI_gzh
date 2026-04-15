import glob, re, os
htmls = glob.glob('output/previews/preview_*.html')
htmls.sort(key=os.path.getmtime, reverse=True)
if htmls:
    h = open(htmls[0], encoding='utf-8').read()
    imgs = [s for s in re.findall(r'src="([^"]+)"', h) if 'png' in s or 'jpg' in s]
    print(f"HTML: {htmls[0]}")
    print(f"Images ({len(imgs)}):")
    for i, img in enumerate(imgs):
        print(f"  [{i}] {img}")
