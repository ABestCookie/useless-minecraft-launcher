import platform
import sys
import os

print("作業系統:", platform.system())          # e.g. 'Windows', 'Linux', 'Darwin' (macOS)
print("版本:", platform.version())              # e.g. OS 版本資訊
print("詳細資訊:", platform.platform())         # e.g. 'Windows-10-10.0.19041-SP0'
print("機器類型:", platform.machine())          # e.g. 'x86_64'
print("處理器:", platform.processor())          # e.g. 'Intel64 Family 6 Model 158 Stepping 10, GenuineIntel'
print("Python 版本:", sys.version)              # e.g. '3.11.4 (main, Jun 7 2023, ...)'
print("目前工作目錄:", os.getcwd())             # 當前的工作目錄



win_ver = sys.getwindowsversion()

print(f"Major: {win_ver.major}, Minor: {win_ver.minor}, Build: {win_ver.build}")

if win_ver.build >= 22000:
    print("這是 Windows 11")
elif win_ver.build >= 10240:
    print("這是 Windows 10")
else:
    print("這是更早版本的 Windows")
