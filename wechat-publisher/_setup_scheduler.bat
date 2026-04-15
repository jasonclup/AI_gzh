@echo off
chcp 65001 >nul
echo ============================================
echo  公众号自动发布 - 定时任务安装器
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=python"
set "AUTO_SCRIPT=%SCRIPT_DIR%_auto_publish.py"

echo [1/4] 检查Python环境...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python并加入PATH
    pause
    exit /b 1
)
echo ✅ Python环境正常

echo.
echo [2/4] 检查自动化脚本...
if not exist "%AUTO_SCRIPT%" (
    echo ❌ 找不到 _auto_publish.py
    pause
    exit /b 1
)
echo ✅ 自动化脚本就绪

echo.
echo [3/4] 创建定时任务...
echo.

:: 删除旧任务（如果存在）
schtasks /delete /tn "公众号早间发布" /f >nul 2>&1
schtasks /delete /tn "公众号午间发布" /f >nul 2>&1
schtasks /delete /tn "公众号晚间发布" /f >nul 2>&1

:: 创建三个定时任务
:: 早间 7:00
schtasks /create /tn "公众号早间发布" /tr "\"%PYTHON_EXE%\" \"%AUTO_SCRIPT%\"" /sc daily /st 07:00 /ru "%USERNAME%" /rl HIGHEST /f
if errorlevel 1 (
    echo ❌ 早间任务创建失败（可能需要管理员权限）
) else (
    echo ✅ 早间发布: 每天 07:00
)

:: 午间 12:30
schtasks /create /tn "公众号午间发布" /tr "\"%PYTHON_EXE%\" \"%AUTO_SCRIPT%\"" /sc daily /st 12:30 /ru "%USERNAME%" /rl HIGHEST /f
if errorlevel 1 (
    echo ❌ 午间任务创建失败
) else (
    echo ✅ 午间发布: 每天 12:30
)

:: 晚间 20:00
schtasks /create /tn "公众号晚间发布" /tr "\"%PYTHON_EXE%\" \"%AUTO_SCRIPT%\"" /sc daily /st 20:00 /ru "%USERNAME%" /rl HIGHEST /f
if errorlevel 1 (
    echo ❌ 晚间任务创建失败
) else (
    echo ✅ 晚间发布: 每天 20:00
)

echo.
echo [4/4] 验证任务...
echo.
echo 当前已配置的定时任务:
echo ----------------------------------------
schtasks /query /fo list | findstr /i "公众号\|TaskName\|Next Run Time\|Status"
echo ----------------------------------------

echo.
echo ============================================
echo  ✅ 定时任务安装完成！
echo ============================================
echo.
echo  系统将每天自动执行3次内容发布：
echo    🌅 07:00 — 早间文章
echo    ☀️ 12:30 — 午间更新  
echo    🌙 20:00 — 晚间推送
echo.
echo  日志位置: wechat-publisher/logs/auto_publish_YYYY-MM-DD.log
echo.
echo  管理命令：
echo    查看任务: schtasks /query /fo list ^| findstr 公众号
echo    手动运行: python _auto_publish.py
echo    删除任务: 以管理员运行本脚本加 --uninstall 参数
echo.
pause
