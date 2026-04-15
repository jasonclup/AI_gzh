# -*- coding: utf-8 -*-
import subprocess, os, sys

OUTPUT = r'c:\Users\v_junshshi\WorkBuddy\Claw\output'
PREVIEW_HTML = os.path.join(OUTPUT, 'article_preview.html')
FULL_PNG = os.path.join(OUTPUT, 'pipeline_preview_full.png')
SCREEN_PNG = os.path.join(OUTPUT, 'pipeline_preview_screen.png')

url = 'file:///' + os.path.abspath(PREVIEW_HTML).replace('\\', '/')
full_path = os.path.abspath(FULL_PNG).replace('\\', '/')
screen_path = os.path.abspath(SCREEN_PNG).replace('\\', '/')

code = f'''
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context()
        # Full page screenshot
        pg = await ctx.new_page()
        await pg.goto('{url}', wait_until='networkidle')
        await pg.screenshot(path='{full_path}', full_page=True)
        await pg.close()
        print('FULL_OK')
        # Viewport screenshot (phone size)
        ctx2 = await browser.new_context(viewport=dict(width=430, height=900))
        pg2 = await ctx2.new_page()
        await pg2.goto('{url}', wait_until='networkidle')
        await pg2.screenshot(path='{screen_path}')
        await pg2.close()
        print('SCREEN_OK')
        await browser.close()

asyncio.run(main())
'''

r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=30)
print('STDOUT:', (r.stdout or '')[-500:])
print('STDERR:', (r.stderr or '')[-300:])

for p in [FULL_PNG, SCREEN_PNG]:
    if os.path.exists(p):
        print(f'OK: {p} ({os.path.getsize(p)//1024}KB)')
    else:
        print(f'MISSING: {p}')
