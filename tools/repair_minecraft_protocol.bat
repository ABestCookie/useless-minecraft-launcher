@echo off
title Minecraft 網路協定修復工具
color 0A

echo.
echo =============================
echo 正在執行 Minecraft 修復流程...
echo =============================
echo.

:: 清除 DNS 快取
echo [1] 清除 DNS 快取...
ipconfig /flushdns

:: 重建 Winsock（修正 socket 錯誤）
echo [2] 重置網路 Winsock 組態...
netsh winsock reset

:: 移除 Minecraft logs 和 session cache（不刪除存檔）
echo [3] 清理 Minecraft 快取資料夾...
cd %APPDATA%\.minecraft
del /f /q .\launcher_log.txt > nul
del /f /q .\usercache.json > nul
del /f /q .\assets\indexes\*.json > nul

:: 結束
echo.
echo 已完成修復建議步驟。
echo 請重新啟動電腦再進行 Minecraft 啟動。
pause
