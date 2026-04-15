import asyncio, glob, os, time
from playwright.async_api import async_playwright

async def full_screenshot():
    htmls = glob.glob('output/previews/preview_*.html')
    htmls.sort(key=os.path.getmtime, reverse=True)
    if not htmls:
        print('No HTML found')
        return
    latest = htmls[0]
    print(f'HTML: {latest}')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 375, 'height': 812})
        # 用 file:// 协议打开（这是用户看到的方式）
        abs_path = os.path.abspath(latest).replace('\\', '/')
        await page.goto(f'file:///{abs_path}', wait_until='networkidle', timeout=20000)
        await page.wait_for_timeout(3000)

        out = f'output/previews/FULL_FIXED_{int(time.time())}.png'
        await page.screenshot(path=out, full_page=True)
        size = os.path.getsize(out) / 1024
        print(f'FULL screenshot: {out} ({size:.0f}KB)')
        await browser.close()

asyncio.run(full_screenshot())
