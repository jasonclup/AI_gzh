"""
独立桌面客户端打包脚本 - 生成完全独立的 .exe（不依赖Python环境）
用法: python build_standalone.py
输出: build_standalone/dist/公众号爆款内容发布系统/ (完整文件夹)
"""
import subprocess, sys, os, shutil, glob, time

# ============================================================
# 配置
# ============================================================
APP_NAME = "公众号爆款内容发布系统"
MAIN_SCRIPT = "desktop_client.py"       # 入口脚本
ICON_FILE = "static/icons/icon-192.png" # 图标(可选)
OUTPUT_DIR = "build_standalone"          # 打包输出目录
DATA_DIRS = [
    ("web", "web"),                      # Web前端代码
    ("modules", "modules"),              # Python功能模块
    ("templates", "templates"),          # HTML模板
    ("static", "static"),                # 静态资源(PWA图标等)
    ("tools", "tools"),                  # 工具模块
    ("output", "output"),                # 输出目录
]
DATA_FILES = [
    ("config.yaml", "."),
    ("requirements.txt", "."),
]

HIDDEN_IMPORTS = [
    # Flask 相关
    "flask", "flask.templating", "flask.logging",
    "jinja2", "jinja2.ext", "markupsafe", "werkzeug", "werkzeug.serving",
    # HTTP请求
    "urllib3", "certifi", "charset_normalizer", "idna",
    # 数据处理
    "yaml", "PIL", "PIL._tkinter_finder",
    "json", "datetime", "random", "re", "os", "sys", "time", "pathlib",
    "html", "html.parser", "html.entities", "bs4", "lxml",
    # Playwright (如果需要截图功能)
    "playwright", "playwright.async_api",
    # 其他模块
    "concurrent", "concurrent.futures",
    "asyncio", "asyncio.tasks",
    "threading", "multiprocessing",
    "logging", "argparse",
    "typing", "dataclasses",
    "copy", "collections", "collections.abc",
    "contextlib", "functools",
    "hashlib", "hmac", "base64",
    "io", "string", "textwrap", "uuid",
    "subprocess", "signal",
    "tempfile", "shutil", "glob", "fnmatch",
    "zipfile", "tarfile",
    "platform", "socket",
    "email", "email.utils",
    "xml.etree.ElementTree",
    "csv", "configparser",
]

EXCLUDE_MODULES = [
    "tkinter", "matplotlib", "numpy", "pandas", "scipy",
    "IPython", "jupyter", "pytest", "sphinx",
    "pydoc", "doctest", "unittest.mock",
    # 减小体积
    "pygments", "setuptools", "distutils",
]


def log(msg):
    """Write to both stdout and log file, handling encoding"""
    safe = msg.encode('ascii', 'replace').decode('ascii') if isinstance(msg, str) else str(msg)
    print(safe)

def build():
    log("=" * 60)
    log(f"  {APP_NAME} - Standalone Desktop Client Build")
    log("=" * 60)
    
    start_time = time.time()
    
    # 清理旧的构建目录
    if os.path.exists(OUTPUT_DIR):
        log(f"\n[1/4] Cleaning old build...")
        try:
            shutil.rmtree(OUTPUT_DIR)
            log("  [OK] Cleaned")
        except Exception as e:
            log(f"  [WARN] Cleanup failed: {e}")
    
    # 收集 data 参数
    datas = []
    for src, dst in DATA_DIRS:
        if os.path.exists(src):
            datas.append((src, dst))
            log(f"  [DIR] {src} -> {dst}")
    
    for src, dst in DATA_FILES:
        if os.path.exists(src):
            datas.append((src, dst))
            log(f"  [FILE] {src} -> {dst}")
    
    if not datas:
        log("\n[ERROR] No source files found! Run from wechat-publisher directory")
        return False
    
    # 构建 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onedir",              # 文件夹模式（比 onefile 更稳定）
        "--windowed",            # 无控制台窗口
        "--clean",
        "--confirm-license-overwrite",
        f"--distpath={OUTPUT_DIR}",
        f"--workpath={OUTPUT_DIR}/build",
        f"--specpath={OUTPUT_DIR}/build",
    ]
    
    # 添加 hidden imports
    for m in HIDDEN_IMPORTS:
        cmd.append(f"--hidden-import={m}")
    
    # 添加 excludes
    for m in EXCLUDE_MODULES:
        cmd.append(f"--exclude-module={m}")
    
    # 添加 data files
    for src, dst in datas:
        cmd.append(f"--add-data={src}{os.pathsep}{dst}")
    
    # 主入口
    cmd.append(MAIN_SCRIPT)
    
    log(f"\n[2/4] Starting build... (1-3 minutes)")
    log(f"  PyInstaller: 6.17.0")
    log(f"  Python: {sys.version.split()[0]}")
    log(f"  Mode: onefolder (standalone)")
    log(f"  Data files: {len(datas)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    if result.returncode != 0:
        log(f"\n[ERROR] Build failed!")
        log(f"STDOUT:\n{result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout}")
        log(f"STDERR:\n{result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr}")
        return False
    
    log(f"\n  [OK] PyInstaller done")
    
    # 创建一键启动 bat
    dist_dir = os.path.join(OUTPUT_DIR, APP_NAME)
    bat_path = os.path.join(dist_dir, "一键启动.bat")
    with open(bat_path, "w", newline="\r\n") as f:
        f.write(f"@echo off\nchcp 65001 >nul\ntitle {APP_NAME}\ncd /d \"%~dp0\"\nstart \"\" \"{APP_NAME}.exe\"\nexit\n")
    
    # 创建使用说明
    readme_path = os.path.join(dist_dir, "使用说明.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# {APP_NAME} v1.0 - 独立桌面版

## 快速开始
1. 双击 **一键启动.bat**
2. 等待 3-5 秒，Edge 浏览器自动打开原生窗口
3. 在窗口中操作所有功能
4. 关闭窗口即可退出

## 特点
- ✅ **完全独立** — 不需要安装 Python 环境
- ✅ **Edge 原生窗口** — 无边框应用模式
- ✅ **系统托盘支持** — 最小化到托盘不占任务栏
- ✅ **所有功能内置** — 抓热点/写文章/配图/预览/发布

## 功能说明
- **热点抓取**: 微博热搜 + 百度实时热榜
- **文章撰写**: AI生成第一人称娱乐性文案（需配置API Key）
- **AI配图**: 自动为每段文字匹配配图（需配置API Key）
- **HTML预览**: 手机端适配的文章预览
- **截图输出**: Playwright渲染完整长图
- **公众号发布**: 一键发布到微信公众号（需配置AppID）

## 配置方法
编辑同目录下的 `config.yaml`：
```yaml
# AI配置（用于文章撰写和图片生成）
AI_MODEL: "gpt-4o"           # 或 deepseek/gpt-4o-mini 等
OPENAI_API_KEY: "sk-xxx"     # 你的 OpenAI API Key
OPENAI_BASE_URL: ...         # API 地址

# 公众号配置
WECHAT_APPID: "wx..."
WECHAT_SECRET: "your_secret"
```

## 注意事项
- 需要 Windows 10/11 系统
- 需要 Edge 或 Chrome 浏览器（Win10/11自带Edge）
- 首次启动可能稍慢（约5-10秒）
- 杀毒软件可能误报，允许运行即可

---
构建时间: {time.strftime('%Y-%m-%d %H:%M')}
版本: v1.0 (Standalone Edition)
""")
    
    elapsed = time.time() - start_time
    
    # 计算总大小
    total_size = 0
    for root, dirs, files in os.walk(dist_dir):
        for f in files:
            fp = os.path.join(root, f)
            total_size += os.path.getsize(fp)
    
    exe_path = os.path.join(dist_dir, f"{APP_NAME}.exe")
    exe_size = os.path.getsize(exe_path) / (1024*1024) if os.path.exists(exe_path) else 0
    
    log(f"\n{'=' * 60}")
    log(f"  [DONE] Build complete!")
    log(f"{'=' * 60}")
    log(f"\n  Output: {os.path.abspath(dist_dir)}")
    log(f"  Total size: {total_size/(1024*1024):.1f} MB")
    log(f"  EXE size: {exe_size:.1f} MB")
    log(f"  Time: {elapsed:.1f}s")
    log(f"\n  How to use:")
    log(f"  1) Go to: {dist_dir}")
    log(f"  2) Double-click: 一键启动.bat")
    log(f"  3) Wait for Edge window to open")
    log(f"{'=' * 60}\n")
    
    return True


if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
