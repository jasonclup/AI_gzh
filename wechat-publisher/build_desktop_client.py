# -*- coding: utf-8 -*-
"""
PyInstaller 打包脚本 - 将公众号发布系统打包为独立 .exe 桌面客户端
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.absolute()
BUILD_DIR = PROJECT_DIR / "build_dist"
DIST_DIR = BUILD_DIR / "dist"
EXE_NAME = "公众号爆款内容发布系统"

def log(msg):
    ts = __import__('time').strftime("%H:%M:%S")
    safe = msg.encode('ascii', 'replace').decode('ascii')
    print(f"[{ts}] {safe}")

log("Start building desktop client")

if BUILD_DIR.exists():
    log("Cleaning old build...")
    shutil.rmtree(BUILD_DIR, ignore_errors=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)

log("Copying project files...")

FILES_TO_COPY = [
    ("web/", "web/"), ("modules/", "modules/"), ("tools/", "tools/"),
    ("templates/", "templates/"), ("static/", "static/"),
    ("output/", "output/"), ("data/", "data/"), ("logs/", "logs/"),
    ("config.yaml", "config.yaml"), ("feishu_bots_config.json", "feishu_bots_config.json"),
    ("server.py", "server.py"), ("desktop_client.py", "desktop_client.py"),
    ("requirements.txt", "requirements.txt"),
]

for src, dst in FILES_TO_COPY:
    src_path = PROJECT_DIR / src
    dst_path = BUILD_DIR / dst
    if src_path.exists():
        if src_path.is_dir():
            if dst_path.exists(): shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        log(f"OK: {src}")
    else:
        log(f"SKIP: {src}")

log("Writing PyInstaller spec file...")
build_path = str(BUILD_DIR).replace('\\', '/')
spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['desktop_client.py'],
    pathex=['{build_path}'],
    binaries=[],
    datas=[
        ('web', 'web'), ('modules', 'modules'),
        ('tools', 'tools'), ('templates', 'templates'),
        ('static', 'static'), ('output', 'output'),
        ('data', 'data'), ('config.yaml', '.'),
        ('feishu_bots_config.json', '.'),
    ],
    hiddenimports=[
        'flask', 'jinja2', 'markupsafe', 'werkzeug',
        'click', 'itsdangerous', 'requests',
        'PIL', 'Pillow', 'yaml', 'json5',
        'playwright', 'asyncio', 'threading',
        'subprocess', 'urllib', 'webbrowser', 'ctypes',
    ],
    hookspath=[], hooksconfig={{}}, runtime_hooks=[],
    excludes=[], noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
    name='{EXE_NAME}', debug=False,
    console=True, strip=False, upx=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, name='{EXE_NAME}')
'''
(BUILD_DIR / f"{EXE_NAME}.spec").write_text(spec_content, encoding='utf-8')

log("Running PyInstaller (this may take 3-5 minutes)...")
os.chdir(str(BUILD_DIR))
r = subprocess.run(
    [sys.executable, "-m", "PyInstaller", "--clean", f"{EXE_NAME}.spec"],
    capture_output=True, text=True, timeout=600,
)

if r.returncode != 0:
    log("PyInstaller FAILED!")
    (BUILD_DIR / "pyi_stderr.txt").write_text(r.stderr or "", encoding='utf-8')
    (BUILD_DIR / "pyi_stdout.txt").write_text(r.stdout or "", encoding='utf-8')
    log("Check pyi_stderr.txt for details")
else:
    log("PyInstaller OK")

exe_path = DIST_DIR / EXE_NAME / f"{EXE_NAME}.exe"
bat_path = DIST_DIR / EXE_NAME / "启动.bat"
if exe_path.exists():
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    log(f"SUCCESS! Exe: {size_mb:.1f} MB")
    bat_path.write_text(f'@echo off\nchcp 65001 >nul\ncd /d "%~dp0"\n"{EXE_NAME}.exe"\npause\n', encoding='utf-8')
    log(f"Launcher bat created at: {bat_path}")
else:
    log("ERROR: exe not found!")
    if DIST_DIR.exists():
        for item in DIST_DIR.rglob("*"):
            if not item.is_dir():
                sz = item.stat().st_size / 1024
                log(f"  {item.relative_to(DIST_DIR)} ({sz:.0f} KB)")

log("Build process complete!")
