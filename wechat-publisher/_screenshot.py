"""截图脚本 - 用playwright截取Flask页面"""
import subprocess, sys, os

# 安装playwright（如果需要）
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing playwright...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium", "-q"])
    from playwright.sync_api import sync_playwright

url = "http://127.0.0.1:8080"
output = os.path.join(os.path.dirname(__file__), "..", "output", "dashboard_screenshot.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    
    # 访问页面
    page.goto(url, timeout=15000)
    page.wait_for_load_state("networkidle", timeout=10000)
    import time; time.sleep(1)
    
    # 截全页
    page.screenshot(path=output, full_page=True)
    print(f"Screenshot saved: {output}")
    
    # 再截一张首页视图
    output2 = output.replace(".png", "_viewport.png")
    page.screenshot(path=output2, full_page=False)
    print(f"Viewport saved: {output2}")
    
    browser.close()
print("DONE")
