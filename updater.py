import os
import sys
import time
import requests
import zipfile
import subprocess
import json




def download_with_resume(url, target_file):
    """ 支援斷點續傳的下載邏輯 """
    temp_file = target_file + ".part"
    initial_pos = os.path.getsize(temp_file) if os.path.exists(temp_file) else 0
    
    headers = {'Range': f'bytes={initial_pos}-'}
    try:
        # stream=True 確保大檔案下載不會塞爆記憶體
        r = requests.get(url, headers=headers, stream=True, timeout=15)
        
        # 416 代表檔案已下載完成或 Range 錯誤
        if r.status_code == 416:
            return True

        total_size = int(r.headers.get('content-length', 0)) + initial_pos
        
        print(f"\n[下載中] 正在獲取資源...")
        
        with open(temp_file, 'ab' if initial_pos > 0 else 'wb') as f:
            downloaded = initial_pos
            for chunk in r.iter_content(chunk_size=1024 * 64): # 64KB chunk
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # CUI 進度條顯示
                    done = int(40 * downloaded / total_size)
                    percent = int(100 * downloaded / total_size)
                    # \r 讓游標回到行首，達成動畫效果
                    sys.stdout.write(f"\r進度: [{'=' * done}{' ' * (40-done)}] {percent}% ({downloaded}/{total_size} bytes)")
                    sys.stdout.flush()
        
        # 下載完成，更名為正式 ZIP
        if os.path.exists(target_file):
            os.remove(target_file)
        os.rename(temp_file, target_file)
        return True
    except Exception as e:
        print(f"\n[錯誤] 下載失敗: {e}")
        return False

def extract_and_install(zip_path):
    """ 解壓縮下載好的包並覆蓋現有檔案 """
    print("\n[安裝中] 正在解壓縮並部署環境...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".") # 解壓至目前目錄
        os.remove(zip_path) # 清理暫存檔
        return True
    except Exception as e:
        print(f"[錯誤] 解壓縮失敗: {e}")
        return False

def main():
    print("========================================")
    print("   Useless Minecraft Launcher Updater   ")
    print("========================================\n")
    
    try:
        # 1. 檢查遠端版本
        print("[檢查] 正在連線至伺服器...")
        resp = requests.get(VERSION_URL, timeout=10)
        data = resp.json()
        remote_version = data['version']
        download_url = data['url']

        # 2. 判斷邏輯 (不存在主程式 = 安裝模式；版本不對 = 更新模式)
        is_installed = os.path.exists(MAIN_EXE)
        needs_update = not is_installed or remote_version > CURRENT_VERSION

        if needs_update:
            status = "安裝" if not is_installed else "更新"
            print(f"[{status}模式] 發現新內容 (版本: {remote_version})")
            
            if download_with_resume(download_url, TEMP_ZIP):
                if extract_and_install(TEMP_ZIP):
                    print("[完成] 部署成功！")
            else:
                print("[中止] 無法完成下載，請檢查網路後重試。")
                input("\n按 Enter 鍵退出...")
                sys.exit()
        else:
            print("[最新] 已是最新版本，無需更新。")

        # 3. 啟動主程式
        if os.path.exists(MAIN_EXE):
            print(f"\n[啟動] 正在開啟 {MAIN_EXE}...")
            # 使用 Popen 啟動後，Updater 就可以自己結束了
            subprocess.Popen([MAIN_EXE], shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit()
        else:
            print("[錯誤] 找不到主程式執行檔，請聯繫作者。")
            input("\n按 Enter 鍵退出...")

    except Exception as e:
        print(f"\n[跳過更新] 無法獲取更新資訊 (可能是離線狀態): {e}")
        if os.path.exists(MAIN_EXE):
            subprocess.Popen([MAIN_EXE])
            sys.exit()
        else:
            input("\n按 Enter 鍵退出...")

if __name__ == "__main__":
    # ================= 設定區 =================
    try:
        with open("app_config/luncher_config.json", "r") as f:
            config = json.load(f)
        VERSION_URL = config["autoupdate"]["url"]  # 你的版本 JSON 網址
        MAIN_EXE = config["main"]["executable"]  # 最終要啟動的主程式
        CURRENT_VERSION = config["main"]["version"]  # 此編譯版本的版本號
        TEMP_ZIP = config["main"]["TEMP_ZIP"]# 下載時的暫存檔名
    except Exception as e:
        print(f"[錯誤] 無法讀取設定檔: {e}")
        VERSION_URL = "https://your-server.com/version.json"  # 你的版本 JSON 網址
        MAIN_EXE = "launcher.exe"                            # 最終要啟動的主程式
                                    # 此編譯版本的
    print(f"當前版本: {CURRENT_VERSION}")
    print(f"版本檢查 URL: {VERSION_URL}")
    print(f"主程式: {MAIN_EXE}")
    print(f"暫存 ZIP: {TEMP_ZIP}")
# ==========================================
    main()