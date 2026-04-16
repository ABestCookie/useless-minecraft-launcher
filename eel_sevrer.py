import eel
import os
import sys
import io
import logging
import subprocess
import app_mod.account as account
import app_mod.skin as skin
import app_mod.server as server
import app_mod.core as core
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
import traceback
import time
import ctypes
import json
import gzip

from winpty import PTY

#cui選單部分
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import Frame, Label
from prompt_toolkit.formatted_text import HTML

# 強制標準輸出使用 UTF-8，啟用 line buffering 避免輸出卡住
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
except AttributeError:
    # 在打包環境中 sys.stdout 可能為 None，跳過重新包裝
    pass
lan_stop=True



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 檔案handler
file_handler = logging.FileHandler("debug.log", mode="w")
file_handler.setLevel(logging.DEBUG)

# 控制台handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 格式器
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)



def show_wan(port):
    sharing_main.destroy()
    call_back = core.other_function.start_ngrok_tunnel(port)
    if call_back != None:
        wan_main = tk.Tk()
        wan_main.title("auto wan sharing tools")
        wan_main.geometry("400x200")
        wan_main.resizable(False, False)
        wan_main.attributes("-topmost", True)
        wan_main.attributes("-topmost", False)   
        tk.Label(wan_main, text=f"已成功為端口 {port} 建立穿透，以下是連接資訊").pack()
        entry = tk.Entry(wan_main, width=50)
        entry.insert(0, call_back)
        entry.config(state='readonly')
        entry.pack()
        tk.Button(wan_main, text="複製連接資訊", command=lambda: [wan_main.clipboard_clear(), wan_main.clipboard_append(call_back), messagebox.showinfo("提示", "已複製到剪貼簿")]).pack()
        wan_main.mainloop()
        lan_stop = False  # 停止局域網穿透偵測
    else:
        messagebox.showerror("錯誤", "建立穿透失敗，請檢查 ngrok 配置或網絡狀態")

def auto_wan_sharing():
    def close():
        global lan_stop
        lan_stop = False
        sharing_main.destroy()
    global lan_stop
    if core.other_function.game_config(mode="load")["ngrok"] == True:
        logger.info("正在啟動局域網穿透偵測...")
        while lan_stop:
            tcp_port = core.other_function.get_all_java_listen_ports()
            if tcp_port != []:
                global sharing_main
                sharing_main = tk.Tk()
                sharing_main.title("auto wan sharing tools")
                sharing_main.geometry("200x300")
                sharing_main.resizable(False, False)
                sharing_main.attributes("-topmost", True)
                sharing_main.attributes("-topmost", False)
                tk.Label(sharing_main, text="請選擇多人遊戲所在port").pack()
                for port in tcp_port:
                    tk.Button(sharing_main, text=port, command=lambda p=port: show_wan(p)).pack()
                tk.Button(sharing_main, text="錯誤偵測?點此取消此進程偵測", command=lambda : close()).pack()
                sharing_main.mainloop()
            else:
                logger.info("未偵測到多人遊戲端口，10秒後重新檢測")
                time.sleep(10)
        
                

def run_command(command):
    # 防呆：命令不能是 None，也不能含有 None 元素
    if command is None:
        raise ValueError("run_command 收到 None 作為命令。")
    if isinstance(command, (list, tuple)):
        for a in command:
            if a is None:
                raise ValueError(f"命令列表中包含 None: {command!r}")
    # 使用 Popen 啟動進程
    global process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # 將錯誤輸出也合併到標準輸出
        text=True,                 # 自動解碼為字串
        bufsize=1,                   # 行緩衝
        encoding='utf-8',              # 指定編碼
        errors='replace'              # 遇到無法解碼的字元時替換為替代字元，避免崩潰
    )
    
    # 即時循環讀取每一行
    for line in process.stdout:
        print(line.strip())
        # 在這裡可以進行日誌寫入文件、GUI 更新或條件判斷

    # 等待進程結束並獲取回傳碼
    return_code = process.wait()
    logger.info(f"進程結束，回傳碼: {return_code}")
    return return_code



@eel.expose
def get_local_ver():
    return core.Launcher.get_local_ver()

@eel.expose
def load_versionSelect(ver):
    
    global select_ver
    select_ver = ver
    logger.debug(f"選擇版本: {select_ver}")
    
def set_status(status: str):
    eel.tip_set_status(status)
    logger.debug(status)


def set_progress(progress: int):
    eel.tip_set_progress(progress)
    if current_max != 0:
        logger.debug(f"{progress}/{current_max}")


def set_max(new_max: int):
    eel.tip_set_max(new_max)
    global current_max
    current_max = new_max
    

    
@eel.expose
def launch_game():
    global lan_stop
    process_bar= {
        "setStatus": set_status,
        "setProgress": set_progress,
        "setMax": set_max
    }
    config=core.other_function.game_config(mode="load")
    logger.debug(config)
    
    # 解析伺服器地址
    server_str=config["server"]
    if server_str != "":
        if ":" not in server_str:
            logging.error(f"無效的伺服器地址格式: {server_str}")
            eel.showMsg("錯誤", f"無效的伺服器地址格式: {server_str}\n請使用 IP:PORT 的格式")
        else:
            server_str = server_str.split(":")
            if len(server_str) == 2:
                server_ip = str(server_str[0])
                try:
                    server_port = int(server_str[1])
                except ValueError:
                    logging.error(f"無效的伺服器端口號碼 : {server_str}")
    else:
        server_ip = None
        server_port = None
    
    # 解析 JVM 參數
    jvm = config.get("jvm", "")
    if jvm:                   # 空字串或 None 都會當成 False
        jvm = jvm.split()
    else:
        jvm = []

    try:
        print("等待完整性驗證...") 
        core.Launcher.install_game(ver=select_ver, Callback=process_bar)
        threading.Thread(target=auto_wan_sharing).start()  # 啟動局域網穿透偵測線程
        cmd = core.Launcher.normal(
            ver=select_ver,
            wide=config["resolution"][0], high=config["resolution"][1],
            memory=config["ram"], executablePath=config["java"],
            server=server_ip, port=server_port, jvm_argv=jvm,
            full_screen=config["fullscreen"]
        )

        if not cmd:  # 包括 None、空清單等
            logging.error(f"Launcher.normal 回傳空命令: {cmd!r}")
            eel.showMsg("錯誤", "無法取得啟動命令，請檢查設定。")
            lan_stop = False  # 停止局域網穿透偵測
            return "遊戲啟動命令錯誤"

        return_code = run_command(cmd)
        lan_stop = False  # 停止局域網穿透偵測
        return f"遊戲啟動成功，回傳碼: {return_code}"
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Failed to launch game: {e}")
        eel.showMsg("啟動失敗", f"無法啟動遊戲：{e}")
        lan_stop = False  # 停止局域網穿透偵測
        return "遊戲啟動失敗"
@eel.expose    
def save_game_config(gameData):
    msg=core.other_function.game_config(mode="save", data=gameData)
    eel.showMsg("提示", msg)
    return 0

@eel.expose    
def html_get_mem():
    return core.total_memory_mb
    
@eel.expose
def html_get_config():
    return core.other_function.game_config(mode="load")
    
@eel.expose
def stop_game():
    global process
    if process and process.poll() is None:  # 檢查進程是否存在且正在運行
        process.terminate()  # 發送終止信號
        try:
            process.wait(timeout=5)  # 等待進程結束
            eel.terminal_show("遊戲進程已成功終止。")
        except subprocess.TimeoutExpired:
            process.kill()  # 強制終止進程
            eel.terminal_show("遊戲進程強制終止。")
    else:
        eel.terminal_show("沒有正在運行的遊戲進程。")
        
@eel.expose
def account_get(mode, name=None):
    if mode == "single":
        return account.read(name)
    elif mode == "list":
        return account.read()
    else:
        return None
    
@eel.expose
def skin_face_get(path, scale=8, include_hat=True):
    return skin.show_minecraft_face_html(path, scale=scale, include_hat=include_hat)

@eel.expose
def dir_open(path):
    if os.path.exists(path):
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])
    else:
        eel.showMsg("錯誤", f"路徑不存在：{path}")

@eel.expose        
def account_write(name, account_type, skin=None):
    result = account.write(name, account_type, skin)
    if isinstance(result, list) and result[0].startswith("E"):
        if result[0] == "E02":
            eel.showMsg("錯誤", f"{result[1]}\n已使用默認皮膚創建帳號。")
        else:
            # 如果返回的是錯誤代碼，顯示錯誤消息
            eel.showMsg("錯誤", result[1])
    elif isinstance(result, list) and result[0].startswith("F"):
        if result[0] == "F01":
            eel.showMsg("錯誤", result[1])
    else:
        # 成功創建帳號，顯示成功消息
        eel.showMsg("成功", f"帳號 '{name}' 已成功創建。")
      
      
@eel.expose  
def updatefilelist():
    return os.listdir("logs/")

@eel.expose
def read_log_file(filename):
    safe_name = os.path.basename(str(filename))
    file_path = os.path.join("logs", safe_name)
    if not os.path.isfile(file_path):
        eel.showMsg("錯誤", f"檔案不存在：{safe_name}")
        return ""
    try:
        if file_path.endswith(".gz"):
            with gzip.open(file_path, "rt", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        eel.showMsg("錯誤", f"讀取檔案失敗：{e}")
        return ""
        
        
def on_close(page, sockets):
    logger.info(f"頁面 {page} 已關閉")
    if not sockets:
        logger.info("所有視窗都關了！準備結束 Python...")
        os._exit(0)


if __name__ == "__main__":
    with open("app_config/electron_path.json", "r") as f:
        electron_path = json.load(f).get("electron_path", "")
        cmd=[electron_path, "."]
    
    def start_eel():
        eel.init(".")
        eel.start('index.html', mode='custom', port=486, close_callback=on_close, cmdline_args=cmd)
    
    start_eel()
    # logger.debug(account_get("single", "WafflyBat"))

