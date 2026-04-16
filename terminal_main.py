import eel
from winpty import PTY
import threading
import os
import sys  # 必須引入 sys 才能重導向輸出
import json

# 初始化 PTY，啟動 cmd.exe
process = PTY(80, 24)
process.spawn("python eel_sevrer.py")  # 啟動後端主程式，這裡可以換成你想啟動的命令

@eel.expose
def send_to_pty(data):
    """接收前端傳來的鍵盤輸入"""
    process.write(data)

def read_from_pty():
    """持續讀取輸出，並在斷線時關閉視窗"""
    while True:
        try:
            
            output = process.read()
            
            if output:
                eel.on_pty_output(output)
                
        except (EOFError, Exception) as e:
            print(f"終端機已斷線: {e}")
            try:
                eel.on_terminal_exit() 
            except:
                pass
            print("正在關閉程式...")
            os._exit(0)  # 強制退出，避免程式繼續運行
            break

@eel.expose
def resize_pty(cols, rows):
    """同步前端與後端的終端機大小"""
    print(f"Resizing PTY to {cols} cols and {rows} rows")
    try:
        process.set_size(cols, rows)
    except Exception as e:
        print(f"Resize Error: {e}")

@eel.expose
def start():
    threading.Thread(target=read_from_pty, daemon=True).start()

eel.init('.')


eel.start('ter.html', size=(800, 600), mode='custom', port=5090, cmdline_args=cmd)