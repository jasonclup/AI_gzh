import asyncio, glob, os, time
from playwright.async_api import async_playwright

async def full_screenshot():
    htmls = sorted(glob.glob('output/previews/preview_*.html'), key=os.path.getmtime, reverse=True)
    if not htmls:
        print('No HTML found')
        return
    latest = htmls[0]
    print(f'HTML: {latest}')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 375, 'height': 812})
        abs_path = os.path.abspath(latest).replace('\\', '/')
        await page.goto(f'file:///{abs_path}', wait_until='networkidle', timeout=20000)
        await page.wait_for_timeout(3000)

        out = f'output/previews/FULL_V3_{int(time.time())}.png'
        await page.screenshot(path=out, full_page=True)
        size = os.path.getsize(out) / 1024
        print(f'FULL screenshot: {out} ({size:.0f}KB)')
        
        # Also check image load status
        imgs = await page.evaluate('''() => {
            const imgs = document.querySelectorAll('.para-img');
            return Array.from(imgs).map(img => ({
                src: img.src,
                naturalWidth: img.naturalWidth,
                complete: img.complete
            }));
        }''')
        for info in imgs:
            w = info.get('naturalWidth', 0)
            ok = 'LOADED' if w > 0 else 'BROKEN'
            src_name = info.get('src', '').split('/')[-1] if info.get('src') else '?'
            print(f'  [{ok}] {src_name} ({w}x{info.get("naturalHeight",0)})')

        await browser.close()

asyncio.run(full_screenshot())
