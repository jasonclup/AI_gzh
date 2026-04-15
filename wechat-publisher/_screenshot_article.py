"""截取文章预览页面的全页截图"""
import subprocess, sys, os, time

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "-q"])
    from playwright.sync_api import sync_playwright

html_file = r"c:\Users\v_junshshi\WorkBuddy\Claw\output\article_preview.html"
output = r"c:\Users\v_junshshi\WorkBuddy\Claw\output\article_preview_full.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 430, "height": 900})  # 手机宽度
    
    url = "file:///" + html_file.replace("\\", "/")
    page.goto(url, timeout=15000)
    page.wait_for_load_state("networkidle", timeout=10000)
    time.sleep(2)  # 等图片加载
    
    # 截全页（长截图）
    page.screenshot(path=output, full_page=True)
    
    # 再截一屏
    output2 = r"c:\Users\v_junshshi\WorkBuddy\Claw\output\article_preview_screen.png"
    page.screenshot(path=output2, full_page=False)
    
    browser.close()
print(f"Full: {output}")
print(f"Screen: {output2}")
print("DONE")
