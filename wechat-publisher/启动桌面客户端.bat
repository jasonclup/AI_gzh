@echo off
chcp 65001 >nul 2>&1
title 🚀 公众号爆款内容发布系统

echo ============================================
echo   🚀 公众号爆款内容发布系统 - 桌面客户端
echo ============================================

cd /d "%~dp0"

echo [1/2] 正在启动 Web 服务...
start /b python server.py >nul 2>&1

echo [2/2] 正在打开客户端窗口...
timeout /t 3 /nobreak >nul

:: 用 Edge 应用模式打开（无边框原生窗口）
start msedge --app=http://127.0.0.1:8080/

echo.
echo ✅ 系统已启动！关闭此窗口会停止服务。
echo    地址: http://127.0.0.1:8080
echo.

:: 保持运行，等待用户关闭
pause
