import eel
import tqdm
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
    filemode="w",
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
    
def set_status(status: str):
    eel.tip_set_status(status)
    print(status)


def set_progress(progress: int):
    eel.tip_set_progress(progress)
    if current_max != 0:
        print(f"{progress}/{current_max}")


def set_max(new_max: int):
    eel.tip_set_max(new_max)
    global current_max
    current_max = new_max
    
@eel.expose
def launch_game():
    process_bar= {
        "setStatus": set_status,
        "setProgress": set_progress,
        "setMax": set_max
    }
    try:
        #eel.tip_test_sequence()
        eel.terminal_show("等待完整性驗證...") 
        core.Launcher.install_game(ver=select_ver, Callback=process_bar)
        cmd=core.Launcher.normal(ver=select_ver)
        return_code = run_command(cmd)
        return f"遊戲啟動成功，回傳碼: {return_code}"
    except Exception as e:
        logging.error(f"Failed to launch game: {e}")
        messagebox.showerror("啟動失敗", f"無法啟動遊戲：{e}")
        return "遊戲啟動失敗"

if __name__ == "__main__":
    eel.init(".")
    eel.start('ui.html', size=(800, 600))

   
