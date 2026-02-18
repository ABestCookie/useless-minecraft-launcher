import ctypes
import tkinter as tk
show_console = True

# 取得 Windows 控制台的視窗控制權
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
def toggle_console(show=True):
    print(f"切換控制台顯示狀態: {'顯示' if show else '隱藏'}")
    # 取得當前控制台視窗句柄
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        if show:
            user32.ShowWindow(hWnd, 5) # 5 = SW_SHOW (顯示)
        else:
            user32.ShowWindow(hWnd, 0) # 0 = SW_HIDE (隱藏)

def on_escape(event):
    global show_console
    show_console = not show_console
    toggle_console(show_console)
    
kernel32.AllocConsole()
toggle_console(False)

root=tk.Tk()
root.title("cmd test")
root.bind("<Escape>", lambda e: on_escape(e))
root.mainloop()

# 注意：使用此方法前，Python 必須曾分配過控制台
# 如果是 --noconsole 打包，可能需要 kernel32.AllocConsole() 先初始化