from imgui_bundle import imgui, immapp
import pyperclip

def gui():
    # 這是你的 ngrok 網址
    public_url = "0.tcp.jp.ngrok.io:12345"

    # 設定 UI 內容
    imgui.text("Minecraft 聯機助手")
    imgui.separator()
    imgui.text(f"網址: {public_url}")

    if imgui.button("點擊複製網址"):
        pyperclip.copy(public_url)
        # 你可以加個狀態顯示「已複製」
    
    if imgui.button("關閉疊層"):
        # 這裡可以直接控制結束程式
        import os
        os._exit(0)

# 啟動應用
# immapp.run 會自動處理視窗建立、置頂邏輯
immapp.run(
    gui_function=gui, 
    window_title="MC Helper Overlay",
    window_size=(300, 150),
    # 這裡可以加入更多參數，例如 window_restore_pos=False
)