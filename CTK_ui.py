import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
import logging
import time
import threading
import json
import app_mod.account as account
import app_mod.skin as skin
import app_mod.server as server
import tkinter.messagebox as messagebox

with open("debug.log", "w") as f:
    f.write("CTK UI log initialized.\n")
logging.basicConfig(
    level=logging.DEBUG,  # 設定最低輸出等級
    filename="debug.log",
    filemode="a",  # 覆蓋用 "w"，追加用 "a"
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("CTK UI 初始化  yoho, america ya!, here is new log beginning")
logging.info("以下為日誌輸出測試")
logging.debug("這是debug信息，通常用於開發時排錯")
logging.info("這是info信息，一般運行時輸出")
logging.warning("這是warning警告")
logging.error("這是error錯誤")
logging.critical("這是critical嚴重錯誤")

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
info_show=True


class LauncherUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x490")
        self.resizable(False, False)
        self.overrideredirect(True)  # 移除原生標題列
        self.attributes("-topmost", True)
        self.focus_force()

        # --- 自訂標題列 ---
        self.titlebar = tk.Frame(self, bg="#eeeeee", height=38)
        self.titlebar.place(x=0, y=0, width=800, height=38)
        
 

        # 最小化按鈕
        min_btn = tk.Label(self.titlebar, text="–", font=("Arial", 16), bg="#eeeeee", fg="#000000", cursor="hand2")
        min_btn.place(x=718, y=7)
         # 最小化按鈕
        def minimize_window(event):
            self.overrideredirect(False)
            self.iconify()
        min_btn.bind("<Button-1>", minimize_window)

        # 還原時自動恢復自訂標題列
        def restore_titlebar(event):
            if self.state() == "normal":
                self.overrideredirect(True)
        self.bind("<Map>", restore_titlebar)

        # 關閉按鈕
        close_btn = tk.Label(self.titlebar, text="✕", font=("Arial", 14), bg="#eeeeee", fg="#000000", cursor="hand2")
        close_btn.place(x=758, y=7)
        close_btn.bind("<Button-1>", lambda e: sys.exit(0))  # 點擊關閉按鈕退出程序
        self.titlebar.place(x=0, y=0, width=800, height=38)

        # 圖示
        icon_img = Image.open("art/java.ico").resize((24, 24))
        self.icon_photo = ImageTk.PhotoImage(icon_img)
        icon_label = tk.Label(self.titlebar, image=self.icon_photo, bg="#eeeeee", bd=0)
        icon_label.place(x=8, y=5)

        # 標題文字
        title_label = tk.Label(
            self.titlebar, text="Useless! Minecraft Launcher v0.1",
            font=("Microsoft JhengHei", 13, "bold"), bg="#eeeeee", fg="#313030"
        )
        title_label.place(x=44, y=8)

    

        

        # 拖曳標題列
        def start_move(event):
            self._drag_start_x = event.x
            self._drag_start_y = event.y
        def do_move(event):
            x = self.winfo_x() + event.x - self._drag_start_x
            y = self.winfo_y() + event.y - self._drag_start_y
            self.geometry(f"+{x}+{y}")
        self.titlebar.bind("<Button-1>", start_move)
        self.titlebar.bind("<B1-Motion>", do_move)
        # 也讓標題文字可拖曳
        title_label.bind("<Button-1>", start_move)
        title_label.bind("<B1-Motion>", do_move)
        icon_label.bind("<Button-1>", start_move)
        icon_label.bind("<B1-Motion>", do_move)

        # --- 內容區域 ---
        # 背景圖
        bg_img = Image.open("art/background.png").resize((800, 490))
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(x=0, y=38, relwidth=1, relheight=1)

         # 左側側邊欄
        sidebar = ctk.CTkFrame(self, width=200, height=452, corner_radius=0)
        sidebar.place(x=0, y=38)

        # 側邊欄內容統一放進一個 frame
        sidebar_inner = ctk.CTkFrame(sidebar, width=180, height=440, fg_color="transparent")
        sidebar_inner.place(x=10, y=0)

        # 標題
        title = ctk.CTkLabel(sidebar_inner, text="Launcher v0.1", font=("Microsoft JhengHei", 14, "bold"))
        title.place(x=0, y=10)

        # 帳戶區塊（改成按鈕）
        # 你可以改成登入/切換帳戶等功能

        account_btn = ctk.CTkButton(
            sidebar_inner,
            width=180, height=60,
            fg_color="#f5f5f5",
            hover_color="#f5f5f5",
            text="",
            command=lambda: account_area(),
            corner_radius=8
        )
        account_btn.place(x=0, y=40)
        self.avatar_photo = skin.show_minecraft_face(f"{os.getcwd()}\\user_data\\skin.png", scale=5, include_hat=True)
        avatar_label = tk.Label(account_btn, image=self.avatar_photo, bd=0)
        avatar_label.place(x=10, y=10)
        ctk.CTkLabel(account_btn, text="WafflyBat", font=("Microsoft JhengHei", 12, "bold")).place(x=60, y=15)
        ctk.CTkLabel(account_btn, text="Microsoft 帳戶", font=("Microsoft JhengHei", 10)).place(x=60, y=35)

        # 遊戲選單
        menu_items = [
            ("實例管理", ""),
            ("實例導覽", ""),
            ("下載", ""),
            ("資源", ""),
            ("設定", ""),
            ("官方網站", "")
        ]
        for i, (text, sub) in enumerate(menu_items):
            btn = ctk.CTkButton(sidebar_inner, text=text, width=180, height=36, fg_color="#e0e0e0", text_color="#222", hover_color="#d0d0d0")
            btn.place(x=0, y=120 + i*45)
            if text == "設定":
                btn.configure(command=lambda: settings_area())
            if sub:
                ctk.CTkLabel(sidebar_inner, text=sub, font=("Microsoft JhengHei", 10), text_color="#888").place(x=120, y=135 + i*45)
        def main_element(state):
            if state == "show":
                sidebar_inner.place(x=10, y=0)
                launch_btn.place(x=540, y=400)
                self.version_menu.place(x=640, y=360)
                if info_show == True:
                    self.tip_frame.place(x=220, y=48)
            elif state == "hide":
                # 隱藏內容
                sidebar_inner.place_forget()
                self.tip_frame.place_forget()  
                launch_btn.place_forget()
                self.version_menu.place_forget()

        def back_to_home(hide_element):
            main_element("show")
            for i in hide_element:
                if isinstance(i, ctk.CTkFrame):
                    i.place_forget()
            logging.info("返回主頁面！")

        def home_button(element, command=None):
            # home_btn 樣式、位置與帳戶按鈕一致
            home_btn = ctk.CTkButton(
                element,
                width=180, height=60,
                fg_color="#f5f5f5",
                hover_color="#f5f5f5",
                text="",
                command=lambda: back_to_home([element, command]),
                corner_radius=8
            )
            home_btn.place(x=0, y=40)  # 與帳戶按鈕相同

            # 圖片與文字
            home_img = Image.open("art/home.png").resize((40, 40))
            self.home_photo = ImageTk.PhotoImage(home_img)  # 避免被垃圾回收
            home_label = tk.Label(home_btn, image=self.home_photo, bd=0, bg="#f5f5f5")
            home_label.place(x=10, y=10)
            ctk.CTkLabel(home_btn, text="主頁", font=("Microsoft JhengHei", 12, "bold"), fg_color="transparent", text_color="#222").place(x=60, y=15)

        def settings_area():
            main_element("hide")  # 隱藏其他內容
            # 顯示設定區域
            logging.info("設定按鈕被點擊！")
            global setting_inner
            setting_inner = ctk.CTkFrame(sidebar, width=180, height=452, fg_color="transparent")
            setting_inner.place(x=10, y=0)  
            home_button(setting_inner)  # 添加主頁按鈕

        def create_account():
            def colse_window():
                window.destroy()
                self.attributes("-topmost", True)  # 恢復主窗口置頂
                self.focus_force()  # 確保主窗口獲得焦點
            window= ctk.CTkToplevel()
            window.title("新增帳戶")
            window.geometry("400x300")
            window.resizable(False, False)  
            window.overrideredirect(True)
            window.attributes("-topmost", True)
            self.attributes("-topmost", False)  # 讓主窗口不再置頂
            window.focus_force()  # 確保新窗口獲得焦點

            def add_skin():
                window.attributes("-topmost", False)  # 讓主窗口不再置頂
                global skin_path
                skin_path = ctk.filedialog.askopenfilename(
                    title="選擇皮膚檔案",
                    filetypes=[("PNG 檔案", "*.png"), ("JPG 檔案", "*.jpg"), ("所有檔案", "*.*")]
                )
                window.attributes("-topmost", True)  # 恢復新窗口置頂
                if skin_path:
                    with open(skin_path, "rb") as r:
                        with open("plugin/mc-skinviewer/skin.png", "wb") as w:
                            w.write(r.read())
                    logging.info(f"皮膚已儲存到 plugin/mc-skinviewer/skin.png")
                    skin_road_display.config(text=f"皮膚路徑：{skin_path}")
            def add_account():
                username = account_name_entry.get().strip()
                if not username:
                    messagebox.showerror("錯誤", "帳戶名稱不能為空！")
                    logging.error("帳戶名稱不能為空！")
                    return
                account_type = "offline"  # 預設為離線帳戶
                event=account.write(username, account_type, skin=skin_path)
                if event == "E01":
                    messagebox.showerror("錯誤", "帳戶已存在！")
                    logging.error("未創建帳戶，帳戶已存在！")
                elif event == "E02":
                    messagebox.showerror("錯誤", "皮膚檔案無效！已使用預設皮膚\n#請重新選擇皮膚檔案#")
                    logging.error("皮膚檔案無效！")
                


            def view_skin():
                server.stop_server()
                threading.Thread(target=server.run_server, args=(f"{os.getcwd()}/plugin/mc-skinviewer",), daemon=True).start()
                os.popen(f"{os.getcwd()}/plugin/app.exe")

            def start_move(event):
                window._drag_start_x = event.x
                window._drag_start_y = event.y

            def do_move(event):
                x = window.winfo_x() + event.x - window._drag_start_x
                y = window.winfo_y() + event.y - window._drag_start_y
                window.geometry(f"+{x}+{y}")

            window.bind("<Button-1>", start_move)
            window.bind("<B1-Motion>", do_move)

            account_name_entry=ctk.CTkEntry(window, placeholder_text="帳戶名稱", width=200)
            account_name_entry.place(x=20, y=50)
            ctk.CTkButton(window, text="新增", command=add_account).place(x=230, y=50)
            skin_road_display = ctk.CTkLabel(window, text="皮膚路徑：", font=("Microsoft JhengHei", 12))
            skin_road_display.place(x=20, y=100)
            ctk.CTkButton(window, text="選取skin", command=add_skin).place(x=75, y=150)
            ctk.CTkButton(window, text="預覽skin", command=view_skin).place(x=225, y=150)
            ctk.CTkButton(window, text="關閉", command=colse_window).place(x=150, y=200)
             

        def account_area():
            main_element("hide")
            logging.info("帳戶按鈕被點擊！")
            global account_inner
            account_inner = ctk.CTkFrame(self, width=580, height=440, corner_radius=0, fg_color="transparent")
            account_inner.place(x=210, y=43)  # 放在主內容區域

            # 新增一個頂部 frame，專門放 home_button
            top_frame = ctk.CTkFrame(sidebar, width=180, height=452, fg_color="transparent")
            top_frame.place(x=10, y= 0)  # 放在左側邊欄位置

            sidebar_item=[
                ("新增離線帳戶", create_account),
                ("新增 Microsoft 帳戶", lambda: print("新增 Microsoft 帳戶功能待實現"))
                ]
            # 在 top_frame 中添加帳戶相關按鈕
            for i , (text, command) in enumerate(sidebar_item):
                btn = ctk.CTkButton(
                    top_frame, text=text, width=180, height=36,
                    fg_color="#e0e0e0", text_color="#222", hover_color="#d0d0d0",
                    command=command
                )
                btn.place(x=0, y=120 + i*45)
            # 把 home_button 放進 top_frame，並配置到和 avatar_label 一樣的位置
            home_button(top_frame, account_inner)  # 這樣 home_btn 會在 top_frame 的 (0,40)，即 account_inner 的 (0,40)

            # 標題
            title = ctk.CTkLabel(account_inner, text="Minecraft 帳戶", font=("Microsoft JhengHei", 16, "bold"))
            title.place(x=210, y=10)  # 標題往右偏，避免和 home_button 重疊

            # 先取得所有帳號名稱
            account_names = account.read()  # 回傳 list
            self.account_avatar_photos = {}  # 防止圖像被GC
            self.account_radio_var = tk.StringVar()
            y_offset = 70  # 下移，避免和頂部 home_button 重疊

            def on_account_select(username):
                # 切換主頁頭像
                user = account.read(username)
                skin_path = user["skin"]["path"]
                self.avatar_photo = skin.show_minecraft_face(skin_path, scale=5, include_hat=True)
                avatar_label.config(image=self.avatar_photo)
                # 你可以在這裡同步切換其他主頁資訊

            for idx, name in enumerate(account_names):
                user = account.read(name)
                frame = ctk.CTkFrame(account_inner, width=540, height=70, fg_color="#fff", corner_radius=12)
                frame.place(x=20, y=y_offset + idx*90)

                # 單選按鈕（左側，垂直置中）
                radio = tk.Radiobutton(
                    frame, variable=self.account_radio_var, value=name,
                    command=lambda u=name: on_account_select(u),
                    bg="#fff", activebackground="#fff"
                )
                radio.place(x=10, y=25)

                # 頭像
                skin_path = user["skin"]["path"]
                self.account_avatar_photos[name] = skin.show_minecraft_face(skin_path, scale=4, include_hat=True)
                avatar = tk.Label(frame, image=self.account_avatar_photos[name], bd=0, bg="#fff")
                avatar.place(x=40, y=10)

                # 名稱與副標
                ctk.CTkLabel(frame, text=name, font=("Microsoft JhengHei", 12, "bold"), text_color="#222", fg_color="transparent").place(x=90, y=12)
                ctk.CTkLabel(frame, text=user["account_type"] + " 帳戶", font=("Microsoft JhengHei", 10), text_color="#888", fg_color="transparent").place(x=90, y=36)

                def delete_account(username):
                    if messagebox.askyesno(
                        "刪除帳戶", f"確定要刪除帳戶 '{username}' 嗎？此帳號將會消失(非常久)。"
                    ) == True:
                        account.delete(username)
                        logging.info(f"帳戶 '{username}' 已被刪除。")
                        frame.destroy()
                        on_account_select(self.account_radio_var.get())  # 切換到剩餘帳戶頭像
                    else:
                        logging.info(f"帳戶 '{username}' 刪除操作已取消。")

                # 右側功能按鈕（仿圖示例，這裡用 emoji 代替，實際可用圖片或自訂圖示）
                btn_x = 340
                icon_btns = [
                    ("🔄", lambda u=name: print(f"刷新 {u}")),
                    ("👤", lambda u=name: print(f"個人資料 {u}")),
                    ("🗑️", lambda u=name: delete_account(u)),
                ]
                for idx2, (icon, cmd) in enumerate(icon_btns):
                    b = tk.Button(frame, text=icon, bd=0, bg="#fff", activebackground="#eee", command=cmd, font=("Segoe UI Emoji", 12))
                    b.place(x=btn_x + idx2*38, y=18, width=32, height=32)

            # 預設選第一個帳號
            if account_names:
                first_user = account_names[0]
                self.account_radio_var.set(first_user)
                on_account_select(first_user)

        def tip_close():
            self.tip_frame.place_forget()
            global info_show
            info_show = False

        # 右上提示框（半透明、可關閉）
        self.tip_frame = ctk.CTkFrame(self, width=600, height=80, fg_color="#FFFFFF", corner_radius=10)
        self.tip_frame.place(x=220, y=48)

        close_btn2 = ctk.CTkButton(
            self.tip_frame, text="✕", width=28, height=28, fg_color="#000000",
            text_color="#888", hover_color="#73FF00", command=lambda: tip_close()
        )
        close_btn2.place(x=540, y=8)

        ctk.CTkLabel(self.tip_frame, text="開發版提示", font=("Microsoft JhengHei", 13, "bold"), text_color="#222").place(x=10, y=5)
        ctk.CTkLabel(
            self.tip_frame,
            text="你正在使用 UMCL 開發版：開發版包含一些實驗性新功能，較為不穩定。",
            font=("Microsoft JhengHei", 10),
            text_color="#444",
            anchor="w",
            justify="left"
        ).place(x=10, y=30)
        logging.warning("[This is not an error message]你正在使用 UMCL 開發版：開發版包含一些實驗性新功能，較為不穩定。")    
        # 啟動遊戲大按鈕
        launch_btn = ctk.CTkButton(
            self, text="啟動遊戲\n1.21.1-Fabric",
            font=("Microsoft JhengHei", 16, "bold"),
            width=220, height=60,
            fg_color="#4caf50", hover_color="#388e3c",
            command=lambda: print("啟動遊戲...")
        )
        launch_btn.place(x=540, y=400)

        # 上拉式選單（放在按鈕右側）
        self.version_menu = ctk.CTkOptionMenu(
            self,
            values=["1.21.1-Fabric", "1.20.6-Forge", "1.19.4-Vanilla"],
            width=120,
            font=("Microsoft JhengHei", 12)
        )
        self.version_menu.set("1.21.1-Fabric")  # 預設選項
        self.version_menu.place(x=640, y=360)
        logging.info("UI 已開啟")   # 位置可依需求微調



        

def main():
    start = time.perf_counter()
    logging.info("啟動 UI...")
    app = LauncherUI()
    rendering = time.perf_counter()
    logging.info(f"UI 渲染時間: {rendering - start} 秒")
    app.mainloop()
    end = time.perf_counter()
    logging.info(f"程序 運行時間: {end - start} 秒")
    logging.info("UI 已關閉")      
if __name__ == "__main__":
   main()