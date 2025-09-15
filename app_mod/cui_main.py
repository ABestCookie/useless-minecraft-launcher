import os
import minecraft_launcher_lib


import threading

def launch_cui_mode(preselected_version=None):
    import subprocess, time
    
    os.system('cls' if os.name == 'nt' else 'clear')

    print(r"""
          _____                    _____                    _____                    _____  
         /\    \                  /\    \                  /\    \                  /\    \ 
        /::\____\                /::\____\                /::\    \                /::\____\
       /:::/    /               /::::|   |               /::::\    \              /:::/    /
      /:::/    /               /:::::|   |              /::::::\    \            /:::/    / 
     /:::/    /               /::::::|   |             /:::/\:::\    \          /:::/    /  
    /:::/    /               /:::/|::|   |            /:::/  \:::\    \        /:::/    /   
   /:::/    /               /:::/ |::|   |           /:::/    \:::\    \      /:::/    /    
  /:::/    /      _____    /:::/  |::|___|______    /:::/    / \:::\    \    /:::/    /     
 /:::/____/      /\    \  /:::/   |::::::::\    \  /:::/    /   \:::\    \  /:::/    /      
|:::|    /      /::\____\/:::/    |:::::::::\____\/:::/____/     \:::\____\/:::/____/       
|:::|____\     /:::/    /\::/    / ~~~~~/:::/    /\:::\    \      \::/    /\:::\    \       
 \:::\    \   /:::/    /  \/____/      /:::/    /  \:::\    \      \/____/  \:::\    \      
  \:::\    \ /:::/    /               /:::/    /    \:::\    \               \:::\    \     
   \:::\    /:::/    /               /:::/    /      \:::\    \               \:::\    \    
    \:::\__/:::/    /               /:::/    /        \:::\    \               \:::\    \   
     \::::::::/    /               /:::/    /          \:::\    \               \:::\    \  
      \::::::/    /               /:::/    /            \:::\    \               \:::\    \ 
       \::::/    /               /:::/    /              \:::\____\               \:::\____\
        \::/____/                \::/    /                \::/    /                \::/    /
         ~~                       \/____/                  \/____/                  \/____/ 
                                                                                            
        CUI Mode - UMCL                                                 By ABestCookie
    """)
    print("初始化 Minecraft 啟動器中...\n")

    # 確認 Minecraft 目錄與版本資料夾存在
    mc_dir = os.path.join(os.getcwd(), ".minecraft")
    versions_dir = os.path.join(mc_dir, "versions")

    if not os.path.exists(versions_dir):
        print("❌ 無法找到 .minecraft/versions 資料夾")
        return

    # 收集版本
    all_versions = sorted([
        d for d in os.listdir(versions_dir)
        if os.path.isdir(os.path.join(versions_dir, d))
    ])

    if not all_versions:
        print("❌ 沒有可用版本，請先安裝")
        return

    # 若帶有版本參數
    if preselected_version:
        if preselected_version not in all_versions:
            print(f"❌ 找不到版本：{preselected_version}")
            return
        version = preselected_version
        print(f"✔ 使用指定版本：{version}")
    else:
        print("=======================================================")
        print("")
        print("可用版本：")
        for idx, ver in enumerate(all_versions):
            print(f" [{idx + 1}] {ver}")
        print("")
        print("註:按ctrl + c 可隨時退出")
        print("=======================================================")

        while True:
            try:
                choice = int(input("請輸入要啟動的版本編號：")) - 1
                if 0 <= choice < len(all_versions):
                    version = all_versions[choice]
                    break
                
                else:
                    print("❗ 請輸入有效的編號")
            except ValueError:
                
               
                print("❗ 請輸入數字")

    print(f"\n✔ 選擇版本：{version}")
    print("檢查與安裝中...")

    try:
        minecraft_launcher_lib.install.install_minecraft_version(
            version, mc_dir,
            callback={
                "setStatus": lambda msg: print(f"[狀態] {msg}"),
                "setProgress": lambda p: None,
                "setMax": lambda m: None
            }
        )
    except Exception as e:
        print(f"❌ 安裝失敗：{e}")
        return

    print("✔ 安裝完成，啟動遊戲...\n")
    bat_path = os.path.join(os.getcwd(), "launch_cmd_temp.bat")

    try:
        proc = subprocess.Popen(
            ["cmd.exe", "/c", bat_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )

        for line in proc.stdout:
            print("> " + line.strip())

        proc.wait()
        print("\n✔ Minecraft 已關閉，歡迎再來！")
        os.system("pause")

    except Exception as e:
        print(f"❌ 無法啟動 Minecraft：{e}")
        os.system("pause")