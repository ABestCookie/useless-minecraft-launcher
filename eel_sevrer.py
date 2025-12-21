import eel
import os
import sys
import logging
import time
import subprocess
import threading
import json
import app_mod.account as account
import app_mod.skin as skin
import app_mod.server as server
import app_mod.core as core
import tkinter.messagebox as messagebox

logging.basicConfig(
    level=logging.DEBUG,
    filename="debug.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s"
)

select_ver="1.21.10"

def run_command(command):
    # 使用 Popen 啟動進程
    global process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # 將錯誤輸出也合併到標準輸出
        text=True,                 # 自動解碼為字串
        bufsize=1                  # 行緩衝
    )
    
    # 即時循環讀取每一行
    for line in process.stdout:
        eel.terminal_show(line.strip())
        # 在這裡可以進行日誌寫入文件、GUI 更新或條件判斷

    # 等待進程結束並獲取回傳碼
    return_code = process.wait()
    return return_code



@eel.expose
def get_local_ver():
    return core.Launcher.get_local_ver()

@eel.expose
def load_versionSelect(ver):
    
    select_ver = ver
    print(select_ver)
    
@eel.expose
def launch_game():
    try:
        core.Launcher.install_game(ver=select_ver)
        cmd=core.Launcher.normal(ver=select_ver)
        return_code=run_command(cmd)
        return f"遊戲啟動成功，回傳碼: {return_code}"
    except Exception as e:
        logging.error(f"Failed to launch game: {e}")
        messagebox.showerror("啟動失敗", f"無法啟動遊戲：{e}")
        return "遊戲啟動失敗"

if __name__ == "__main__":
    eel.init(".")
    eel.start('ui.html', size=(800, 600))

   
