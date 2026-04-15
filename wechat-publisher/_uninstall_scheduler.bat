@echo off
chcp 65001 >nul
echo ============================================
echo  公众号自动发布 - 定时任务卸载器
echo ============================================
echo.

schtasks /delete /tn "公众号早间发布" /f >nul 2>&1 && echo ✅ 已删除: 公众号早间发布
schtasks /delete /tn "公众号午间发布" /f >nul 2>&1 && echo ✅ 已删除: 公众号午间发布
schtasks /delete /tn "公众号晚间发布" /f >nul 2>&1 && echo ✅ 已删除: 公众号晚间发布

echo.
echo 所有定时任务已清除。
pause
