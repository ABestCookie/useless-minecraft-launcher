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
        core.Launcher.normal(ver=select_ver)
        subprocess.Popen("launch_cmd_temp.bat")
        return "遊戲啟動成功"
    except Exception as e:
        logging.error(f"Failed to launch game: {e}")
        messagebox.showerror("啟動失敗", f"無法啟動遊戲：{e}")
        return "遊戲啟動失敗"

if __name__ == "__main__":
    eel.init(".")
    eel.start('ui.html', size=(800, 600))

   
