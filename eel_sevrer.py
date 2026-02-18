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
import traceback

# 強制標準輸出使用 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


logging.basicConfig(
    level=logging.DEBUG,
    filename="debug.log",
    filemode="w",
    format="%(asctime)s [%(levelname)s] %(message)s"
)

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
        eel.terminal_show(line.strip())
        # 在這裡可以進行日誌寫入文件、GUI 更新或條件判斷

    # 等待進程結束並獲取回傳碼
    return_code = process.wait()
    print(f"進程結束，回傳碼: {return_code}")
    return return_code



@eel.expose
def get_local_ver():
    return core.Launcher.get_local_ver()

@eel.expose
def load_versionSelect(ver):
    
    global select_ver
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
    config=core.other_function.game_config(mode="load")
    
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
        eel.terminal_show("等待完整性驗證...") 
        core.Launcher.install_game(ver=select_ver, Callback=process_bar)

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
            return "遊戲啟動命令錯誤"

        return_code = run_command(cmd)
        return f"遊戲啟動成功，回傳碼: {return_code}"
    except Exception as e:
        traceback.print_exc()
        logging.error(f"Failed to launch game: {e}")
        eel.showMsg("啟動失敗", f"無法啟動遊戲：{e}")
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
    
        
def on_close(page, sockets):
    print(f"頁面 {page} 已關閉")
    if not sockets:
        print("所有視窗都關了！準備結束 Python...")
        os._exit(0)
@eel.expose        
def ok():
    root.withdraw()

if __name__ == "__main__":
    cmd=[r"C:\Users\tsai cookie\Documents\GitHub\useless-minecraft-launcher\ui\chrome-win\chrome.exe",
         "--app=http://localhost:486/index.html",
         "--window-size=900,700"]
    
    def start_eel():
        eel.init(".")
        eel.start('index.html', mode='custom', port=486, cmdline_args=cmd, close_callback=on_close)
    
    
    root = tk.Tk()
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    width, height = 300, 200
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2) #window致中
    root.geometry(geometry)
    root.title("啟動器服務器")
    root.overrideredirect(True)
    t1=tk.Label(root, text="UI啟動中...", font=("Arial", 12))
    t1.pack(expand=True)
    threading.Thread(target=start_eel).start()
    root.mainloop()
    
    #print(account_get("single", "WafflyBat"))

