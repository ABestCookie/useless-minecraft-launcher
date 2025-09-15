import tkinter as tk

def fake_bsod():
    """顯示假 BSOD 當機畫面"""
    root = tk.Tk()
    root.attributes("-fullscreen", True)  # 全螢幕
    root.configure(bg="blue")  # Windows 藍屏背景
    root.overrideredirect(True)  # 移除視窗控制按鈕
    label = tk.Label(root, text="Your PC ran into a problem and needs to restart.\n\n"
                                "We're just collecting some error info, and then we'll restart for you.\n\n"
                                "0% complete",
                     fg="white", bg="blue", font=("Consolas", 20), justify="left")
    label.pack(pady=200)
    root.mainloop()

fake_bsod()
