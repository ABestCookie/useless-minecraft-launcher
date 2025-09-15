import os, sys, tkinter, threading, webbrowser, json
import  tkinter.filedialog, tkinter.messagebox, tkinter.ttk, tkinter.scrolledtext
import minecraft_launcher_lib
import app_mod.core as core
#from tkinter.ttk import *
from tkinter import *
from tkinter import ttk
import tkinter as tk

import datetime
import subprocess
import threading


#僕は大好きアーリャさん着る"彼シャツ"
#Boku wa daisuki ārya-san kiru" kare shatsu"
width = 800
height = 600

def install_in_thread(version: str):
    def run_install():
        set_status(f"準備安裝 Minecraft {version}")
        minecraft_launcher_lib.install.install_minecraft_version(
            version, core.minecraft_directory, callback=callback
        )
        set_status("✔ 安裝完成")
        set_max(0)

        # 執行 .bat 啟動遊戲（非同步）
        threading.Thread(target=run_game_from_batch, daemon=True).start()

    threading.Thread(target=run_install, daemon=True).start()

def run_game_from_batch():
    try:
        # 使用 bat 路徑（當前資料夾底下）
        bat_path = os.path.join(os.getcwd(), "launch_cmd_temp.bat")

        # 執行 bat，非同步並收集輸出
        process = subprocess.Popen(
            ["cmd.exe", "/c", bat_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=os.getcwd()  # 保險起見指定工作資料夾
        )

        output_lines = []
        for line in process.stdout:
            output_lines.append(line)

        process.wait()
        full_output = "".join(output_lines)

        # 呼叫分析函式
        analyze_and_show_log(full_output)

    except Exception as e:
        print("❌ 執行 bat 發生錯誤：", e)
        analyze_and_show_log(f"啟動失敗：{e}")

#安裝進度回傳
current_max = 0

def set_status(status: str):
    print(f"[狀態] {status}")

    # 更新任務標籤
    if "task_label" in globals():
        task_label["text"] = f"任務：{status.strip()}"

    # 特別處理 Java 安裝階段
    if "Install java runtime" in status and "bar" in globals():
        if str(bar["mode"]) != "indeterminate":
            bar.config(mode="indeterminate")
            bar.start()

    # 如果目前沒有 max 也進 indeterminate 模式
    if current_max == 0 and "bar" in globals():
        if str(bar["mode"]) != "indeterminate":
            bar.config(mode="indeterminate")
            bar.start()

def set_progress(progress: int):
    if current_max != 0:
        percent = int(progress / current_max * 100)
        if "bar" in globals():
            if str(bar["mode"]) == "indeterminate":
                bar.stop()
                bar.config(mode="determinate")
            bar["value"] = percent
            bar.update_idletasks()
        if "progress_label" in globals():
            progress_label["text"] = f"安裝進度：{percent}%"

def set_max(new_max: int):
    global current_max
    current_max = new_max
    if "bar" in globals():
        if new_max == 0:
            bar.config(mode="indeterminate")
            bar.start()
        else:
            bar.stop()
            bar.config(mode="determinate", maximum=100)
            bar["value"] = 0
            bar.update_idletasks()
    if "progress_label" in globals():
        progress_label["text"] = "安裝進度：0%"
    if "task_label" in globals():
        task_label["text"] = "目前沒有任務"





callback = {
    "setStatus": set_status,
    "setProgress": set_progress,
    "setMax": set_max
}

try:
    with open("user_data/common.json", "r") as r:
            
        common_option=json.loads(r.read())
except:
    with open("user_data/common.json", "w") as w:
        data={"toggle":False, "ver":None}
        json.dump(data, w, indent=2)
            
        common_option=data


def check_minecraft_log(text: str) -> dict:
    """
    分析 Minecraft 執行輸出內容，回傳結構化結果。
    回傳格式：
    {
        "狀態": "正常" | "異常" | "啟動失敗" | "不明",
        "關鍵詞": "Shutting down internal server" | "java.lang.NullPointerException" | ...
    }
    """
    text_lower = text.lower()

    分類關鍵詞 = {
        "正常": [
            "stopping server", "shutting down", "saving chunks", "saving worlds", "goodbye"
        ],
        "異常": [
            "exception", "stacktrace", "crash", "error", "exit code", "java.lang", "caused by",
            "traceback", "fatal", "panic"
        ],
        "啟動失敗": [
            "launching failed", "failed to launch", "invalid version", "missing", "could not find",
            "launchwrapper", "launch error"
        ]
    }

    # 檢查分類
    for 狀態, 關鍵字列表 in 分類關鍵詞.items():
        for kw in 關鍵字列表:
            if kw in text_lower:
                # 回傳原始關鍵詞（從原始文字中提取一行供參考）
                for line in text.splitlines():
                    if kw in line.lower():
                        return {
                            "狀態": 狀態,
                            "關鍵詞": line.strip()
                        }

    return {
        "狀態": "不明",
        "關鍵詞": "未偵測到明確結束訊息"
    }

def analyze_and_show_log(log_text: str):
    result = check_minecraft_log(log_text)
    status = result["狀態"]
    message = result["關鍵詞"]

    # 讀取設定
    try:
        with open("user_data/launcher_config.json", "r") as f:
            config = json.load(f)
            show_log = config.get("show_log_on_launch", False)
    except:
        show_log = False

    # 要不要顯示日誌視窗？
    should_show_log = show_log or (status != "正常")

    if should_show_log:
        CommandWindow(log_text)

    # 顯示對應訊息
    if status == "正常":
        tkinter.messagebox.showinfo("UMCL", f"Minecraft 已正常結束。\n關鍵：{message}")
    elif status == "異常":
        tkinter.messagebox.showerror("UMCL", f"⚠ Minecraft 運行出錯\n{message}")
    elif status == "啟動失敗":
        tkinter.messagebox.showerror("UMCL", f"❌ Minecraft 啟動失敗\n{message}")
    else:
        tkinter.messagebox.showwarning("UMCL", f"⚠ 無法判斷 Minecraft 是否正常結束\n（{message}）")


class CommandWindow:
    def __init__(self, log_text: str):
        self.log_text = log_text

        # 創建新視窗
        self.window = tk.Toplevel()
        self.window.title("Minecraft 啟動日誌")
        self.window.geometry("600x400")

        # 設定選單
        self.menu = Menu(self.window)
        self.menu.add_command(label="保存日誌檔", command=self.save_log)
        self.window.config(menu=self.menu)

        # 顯示區域
        self.text_area = tkinter.scrolledtext.ScrolledText(self.window, wrap=tk.WORD, font=("Courier", 10))
        self.text_area.pack(expand=True, fill="both")

        self.text_area.insert(tk.END, self.log_text)
        self.text_area.yview(tk.END)

    def save_log(self):
        outputfilename = "minecraft_log_output"
        filepath = tkinter.filedialog.asksaveasfilename(
            parent=self.window,
            initialdir=core.home_path,
            filetypes=(("Log日誌檔", "*.log"), ("All Files", "*.*")),
            initialfile=f"{outputfilename}.log"
        )

        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.log_text)
                f.write("\n")
                f.write(f"[generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        except Exception as e:
            print("❌ 無法保存日誌檔案：", e)


class configwindow:
    def __init__(self, event=None):
        self.window = Toplevel()
        self.window.title("設定")
        self.window.geometry("300x200")

        self.show_log_var = tk.BooleanVar()

        # 載入現有設定
        try:
            with open("user_data/launcher_config.json", "r") as f:
                config = json.load(f)
                self.show_log_var.set(config.get("show_log_on_launch", False))
        except:
            self.show_log_var.set(False)

        # 建立 Checkbutton
        self.check = tk.Checkbutton(self.window, text="啟動時顯示日誌", variable=self.show_log_var, command=self.toggle_show_log)
        self.check.pack(pady=10)
        # 建立記憶體調整滑塊
        tk.Label(self.window, text="記憶體調整(MB)").pack(pady=5)
        self.input_memory = tk.Entry(self.window, width=20, justify='center')
        self.input_memory.pack(pady=5)
        self.input_memory.insert(0, "1536")  # 預設值為1536MB
          # 預設值為1536MB
        self.memory_scale=tk.Scale(self.window, from_=128, to=core.total_memory_mb, orient='horizontal', length= 250, command=self.get_memory)
        self.memory_scale.set(1536)  # 預設值為1536MB
        self.memory_scale.pack(pady=5)

    def toggle_show_log(self):
        # 儲存設定
        config = {"show_log_on_launch": self.show_log_var.get()}
        with open("user_data/launcher_config.json", "w") as f:
            json.dump(config, f, indent=2)
    def get_memory(self, event=None):
        print(f"(debug)記憶體調整為: {self.memory_scale.get()} MB")
        self.input_memory.delete(0, tk.END)  # 清除現有內容
        self.input_memory.insert(0, str(self.memory_scale.get()))  # 插入新的
        global memory
        # 儲存記憶體設定
        memory= self.memory_scale.get()



class UWPwindow:
    def __init__(self, event=None):
        self.app_name=None
        with open("user_data/MC_UWPid_lib.json", "r") as r:
            self.data=json.loads(r.read())
        self.main=Toplevel()
        self.main.title("開啟UWP應用")
        self.main.geometry("400x300")
        self.check_var = tk.BooleanVar()
        self.check_var.set(0)  # 預設為未選取
        self.options = self.data["edition"]
        self.combo = ttk.Combobox(self.main, values=self.options)
        self.combo.pack(pady=5)
        self.bt1=Button(self.main, text="Launch!", command=self.launch)
        self.bt1.pack()
        self.combo.bind("<<ComboboxSelected>>", self.on_select)
    
    def open_UWP(self, app_name:str):
        # 使用 subprocess 開啟 UWP 應用程式
        
        if (app_name == None) == False:
            
            subprocess.Popen(f"start shell:AppsFolder\{self.data[app_name]}", shell=True)

    
    def on_select(self, event=None):
        
        self.selected_value = self.combo.get()
        print(f"你選擇了: {self.selected_value}")
    
    def launch(self):
        self.open_UWP(app_name=self.selected_value)
        
    class aboutwindow(Toplevel):
        def __init__(self, event=None):
            super().__init__()
            self.title("關於UMCL")
            self.geometry("200x200")

    

    
        

def save_bat(event=None):
    alya = core.Launcher()
    #判斷有沒有選擇版本
    try:
        if (selected_value == None) == False:
                ver=selected_value

        elif (common_option["ver"] == None) == False:
            ver=common_option["ver"]
        else:
            ver=options[0]
    except:
        ver=options[0] 

    alya.normal(ver, width, height, False, "WafflyBat")
    outputfilename=f"{ver} export"#設定檔名
    filepath=tkinter.filedialog.asksaveasfilename(initialdir=core.home_path, #初始目錄
                                                      filetypes=(("Windows 批次檔案", "*.bat"), ("all files", "*.*")), #檔案類型設定
                                                      initialfile=f"{outputfilename}.bat") #檔名設定
    if not filepath:
        pass
    else:
        try:
            with open(filepath, "w") as f:
                f.write("@echo off\ncolor 2\n")
                f.write(f"echo 準備運行{ver}\n")
                with open("launch_cmd_temp.bat", "r") as rdf:
                    f.write(rdf.read())
                    f.write("\n")
                f.write("pause")               

        except:
            print("路徑錯誤")

#play!
def play():
    
    alya = core.Launcher()
    
    
    yn=tkinter.messagebox.askyesno("UMCL", "Do you want to play Minecraft?")
    if yn == True:
        #判斷有沒有選擇版本
        try:
            if (selected_value == None) == False:
                ver=selected_value
                
            elif (common_option["ver"] == None) == False:
                ver=common_option["ver"]
            else:
                ver=options[0]
        except:
            ver=options[0] 

        alya.normal(ver, width, height, "WafflyBat", memory=memory)
        print("準備運行 : ", ver)
        #以下是安裝minecraft版本的，會自動下載並安裝指定版本的minecraft
        install_in_thread(ver)
        
def on_select(event=None):
    global selected_value
    selected_value = combo.get()
    print(f"你選擇了: {selected_value}")
    with open("user_data/common.json", "w") as w:
        common_option["ver"]=selected_value
        json.dump(common_option, w, indent=2)

def disable_close(event=None):
    yn=tkinter.messagebox.askyesno("UMCL", "是否關閉啟動器")
    if yn == True:
        
        sys.exit(0)
    else:
        pass

def main_app():
    
    global main

    #check system
    

    

    main=Tk()
    main.title("UMCL")
    screenwidth = main.winfo_screenwidth()
    screenheight = main.winfo_screenheight()
    geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2) #window致中
    main.geometry(geometry)
    main.resizable(width=False, height=False)
    main.protocol("WM_DELETE_WINDOW", disable_close)
    icon_path = os.path.join(os.getcwd() + "\\art\\", "java.ico")
    if os.path.exists(icon_path):
        main.iconbitmap(icon_path)
    else:
        print("Warning: Icon file not found")
    #vbar = Notebook(main).pack()
    按鈕一號=Button(text="launcher game", command=play).pack()

    global check_var
    check_var = tk.BooleanVar()
    check_var.set(common_option["toggle"])  # 預設為未選取
    

    #創建頂部菜單(menubar)
    menu=Menu(main)
    file_menu=Menu(menu, tearoff=0)
    
    music_menu=Menu(menu, tearoff=0)
    config_menu=Menu(menu, tearoff=0)
    game_menu=Menu(menu, tearoff=0)
    menu.add_cascade(label="檔案", menu=file_menu)
    file_menu.add_command(label="保存啟動腳本", command=save_bat, accelerator="按 Alt + O 開啟")

    menu.add_cascade(label="基岩版啟動", menu=game_menu)
    if core.system_check() == True:
        game_menu.add_checkbutton(label="啟動本地", command=UWPwindow, accelerator="按 Alt + U 開啟")
    if core.system_check() == False:
        game_menu.add_checkbutton(label="啟動本地", command=UWPwindow, accelerator="系統不支持", state="disabled")

    menu.add_cascade(label="設定", menu=config_menu)
    config_menu.add_command(label="開啟設定", command=configwindow, accelerator="按 Alt + I 開啟")
    config_menu.add_separator()
   

    menu.add_command(label="離開", command=disable_close)

    main.bind_all("<Alt-o>", save_bat)
    main.bind_all("<Alt-i>", configwindow)
    
    main.bind("<Alt-F4>", disable_close)
    main.bind_all("<Alt-u>", UWPwindow)

    main.config(menu=menu)

    # 創建下拉式選單
    global options, combo
    options = core.Launcher.get_local_ver()
    combo = ttk.Combobox(main, values=options)
    combo.pack(pady=5)
    
    # 創建Progressbar
    global bar
    bar = ttk.Progressbar(main, maximum=100, length=width - 20, mode='determinate')
    bar.pack(pady=20, side=tk.BOTTOM)
    #安裝進度標籤
    global progress_label
    progress_label = tk.Label(main, text="安裝進度：0%")
    progress_label.pack(pady=5, side=tk.BOTTOM)
    #進度標籤
    global task_label
    task_label = tk.Label(main, text="", anchor="w")
    task_label.pack(pady=(10, 0), side=tk.BOTTOM)
    task_label.pack_forget()  # 先隱藏



    # 設定預設值
    combo.current(0)  # 預設選擇第一個選項

    # 綁定選擇事件
    combo.bind("<<ComboboxSelected>>", on_select)

    main.mainloop()