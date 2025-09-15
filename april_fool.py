import tkinter as tk
import random
import sys
import pyautogui
import os
import time
import threading

def follow_mouse():
    """讓視窗一直跟隨滑鼠位置"""
    x, y = pyautogui.position()  # 獲取滑鼠當前座標
    root.geometry(f"300x200+{x}+{y}")  # 移動視窗到滑鼠位置
    root.after(50, follow_mouse)  # 每 50ms 更新一次位置

def move_window(event=None):
    """當使用者嘗試點擊視窗時，讓它隨機移動"""
    x = random.randint(100, 800)
    y = random.randint(100, 500)
    root.geometry(f"550x250+{x}+{y}")




def fake_close():
    """當使用者點擊關閉按鈕時，打開新的視窗"""
    new_window = tk.Toplevel(root)
    new_window.geometry("300x200")
    new_window.title("哈哈，你上當了！")
    
    label = tk.Label(new_window, text="你以為可以關掉我嗎？😂", font=("Arial", 12))
    label.pack(pady=20)

    threading.Thread(target=glitch_screen, daemon=True).start()
    # 啟動滑鼠跟隨功能
    follow_mouse()
    # 綁定視窗移動事件
    new_window.bind("<Enter>", move_window)
    root.overrideredirect(True)  # 移除視窗控制按鈕
    new_window.bind("<x>", real_close)
    
    

def disable_close():
    """讓視窗無法用正常方式關閉"""
    fake_bsod() #假藍屏
    pass  # 什麼都不做，阻止窗口被關閉
def real_close(event=None):
    sys.exit()

def glitch_screen():
    """製造全螢幕花屏效果"""
    while True:
        # 創建全螢幕視窗
        glitch = tk.Toplevel()
        glitch.attributes("-fullscreen", True)
        glitch.attributes("-topmost", True)  # 確保在最前面
        
        # 隨機背景色
        color = random.choice(["red", "green", "blue", "yellow", "magenta", "cyan", "black", "white"])
        glitch.configure(bg=color)
        
        # 閃爍 0.1 秒
        glitch.update()
        time.sleep(0.1)
        glitch.destroy()
def bsod_close(event=None):
    froot.destroy()
    fake_close()

    """關閉假藍屏"""
    

def fake_bsod():
    global froot
    froot = tk.Toplevel()
    froot.attributes("-fullscreen", True)
    froot.configure(bg="blue")
    
    error_label = tk.Label(froot, text=":P  Your PC ran into a problem and needs to restart.\n\n"
                                   "We're just collecting some error info, and then we'll restart for you.\n\n\n\n"
                                   "pan needer\n\n"
                                   "如果我不講你就重啟了:p\n\n"
                                   "按f關掉，或著下面按鈕也行",
                           fg="white", bg="blue", font=("Consolas", 20), justify="left")
    error_label.pack(pady=50)

    progress = tk.Label(froot, text="0% complete", fg="white", bg="blue", font=("Consolas", 20))
    progress.pack()

    def update_progress():
        for i in range(1, 101, random.randint(5, 15)):
            progress.config(text=f"{i}% complete")
            froot.update()
            time.sleep(random.uniform(0.3, 0.8))
        progress.config(text="100% complete\nRebooting now...")
        time.sleep(2)
        bsod_close()

    
    froot.bind("<f>", bsod_close)
    froot.bind("<x>", real_close)

    threading.Thread(target=update_progress, daemon=True).start()

    
    
    

# 主視窗
root = tk.Tk()
root.geometry("800x500")




root.title("updater")


icon_path = os.path.join(os.path.dirname(__file__) + "\\art\\", "java.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
else:
    print("Warning: Icon file not found")

# 標籤
label = tk.Label(root, text="""
██╗░░░██╗██████╗░██████╗░░█████╗░████████╗███████╗
██║░░░██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝
██║░░░██║██████╔╝██║░░██║███████║░░░██║░░░█████╗░░
██║░░░██║██╔═══╝░██║░░██║██╔══██║░░░██║░░░██╔══╝░░
╚██████╔╝██║░░░░░██████╔╝██║░░██║░░░██║░░░███████╗
░╚═════╝░╚═╝░░░░░╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝
""", font=("Arial", 12))
label.pack(pady=20)

# 關閉按鈕
close_btn = tk.Button(root, text="close", command=fake_close)
close_btn.pack()

# 讓視窗無法被正常關閉
root.protocol("WM_DELETE_WINDOW", disable_close)
root.bind("<Alt-F4>", lambda e: "break")  # 阻止 Alt+F4




root.bind("<x>", real_close)

# 啟動主迴圈
root.mainloop()

#2025.3.30 16:51 done