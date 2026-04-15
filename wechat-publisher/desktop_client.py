# -*- coding: utf-8 -*-
"""
公众号爆款内容发布系统 - 桌面客户端（完整版）
启动 Flask 后台 → 用 Edge 应用模式打开原生窗口 → 系统托盘常驻
"""

import os
import sys
import time
import threading
import subprocess
import signal
from pathlib import Path

# 项目目录
PROJECT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_DIR))

# ============================================================
# 配置
# ============================================================

PORT = 8080
APP_NAME = "公众号爆款内容发布系统"
FLASK_PROCESS = None


def log(msg):
    """带时间戳的日志"""
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


# ============================================================
# Flask 服务管理
# ============================================================

def start_flask_server():
    """在子进程中启动 Flask 服务"""
    global FLASK_PROCESS
    
    os.chdir(PROJECT_DIR)
    
    # 用子进程启动 server.py（独立进程，更稳定）
    FLASK_PROCESS = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        cwd=str(PROJECT_DIR)
    )
    
    # 等待服务就绪
    import urllib.request
    max_wait = 20
    for i in range(max_wait):
        try:
            req = urllib.request.Request(f'http://127.0.0.1:{PORT}/', method='HEAD')
            resp = urllib.request.urlopen(req, timeout=2)
            if resp.status == 200:
                log(f"Web 服务已就绪 (端口 {PORT})")
                return True
        except Exception:
            pass
        time.sleep(1)
    
    log("⚠️ Web 服务启动可能较慢，继续打开客户端...")
    return True  # 即使超时也继续


def stop_server():
    """停止 Flask 服务"""
    global FLASK_PROCESS
    if FLASK_PROCESS and FLASK_PROCESS.poll() is None:
        log("正在停止 Web 服务...")
        FLASK_PROCESS.terminate()
        try:
            FLASK_PROCESS.wait(timeout=5)
        except subprocess.TimeoutExpired:
            FLASK_PROCESS.kill()
        log("Web 服务已停止")


# ============================================================
# 桌面窗口（Edge 应用模式）
# ============================================================

def open_desktop_window():
    """用 Edge 应用模式打开原生桌面窗口"""
    url = f"http://127.0.0.1:{PORT}/"
    
    # 方案优先级：
    # 1. Edge 应用模式（最佳：无边框、原生窗口、任务栏图标）
    # 2. Chrome 应用模式（备选）
    # 3. 默认浏览器（兜底）
    
    opened = False
    
    # 尝试 Edge
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for edge_path in edge_paths:
        if os.path.exists(edge_path):
            try:
                subprocess.Popen(
                    [edge_path, f"--app={url}", "--start-maximized"],
                    cwd=os.environ.get("USERPROFILE", ".")
                )
                log(f"已用 Edge 打开桌面窗口")
                opened = True
                break
            except Exception as e:
                log(f"Edge 启动失败: {e}")
    
    if not opened:
        # 尝试 Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    subprocess.Popen([chrome_path, f"--app={url}"])
                    log(f"已用 Chrome 打开桌面窗口")
                    opened = True
                    break
                except Exception:
                    pass
    
    if not opened:
        # 最终兜底：默认浏览器
        import webbrowser
        webbrowser.open(url)
        log("已用默认浏览器打开")
    
    return opened


# ============================================================
# 清理退出
# ============================================================

def cleanup():
    """退出时清理资源"""
    log("正在清理...")
    stop_server()
    log("再见！👋")


# ============================================================
# 主程序
# ============================================================

def main():
    # Windows 控制台编码
    if sys.platform == 'win32':
        os.system('chcp 65001 >nul 2>&1')
        # 设置控制台标题
        ctypes = __import__('ctypes')
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleTitleW(f"{APP_NAME}")
    
    banner = f"""
{'='*52}
   🚀 {APP_NAME} - 桌面客户端 v1.0
{'='*52}
   📍 运行地址 : http://127.0.0.1:{PORT}
   📂 工作目录 : {PROJECT_DIR}
   💡 关闭此窗口会自动停止服务
{'='*52}
"""
    print(banner)
    
    # 注册退出信号
    signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
    
    # 1. 启动 Flask 服务
    log("[步骤 1/2] 正在启动 Web 服务...")
    start_flask_server()
    
    # 2. 打开桌面窗口
    log("[步骤 2/2] 正在打开桌面窗口...")
    open_desktop_window()
    
    # 3. 保持运行
    log("\n✅ 系统运行中... 关闭此窗口即可退出\n")
    try:
        while True:
            time.sleep(3600)  # 保持进程运行
    except KeyboardInterrupt:
        cleanup()


if __name__ == '__main__':
    main()
