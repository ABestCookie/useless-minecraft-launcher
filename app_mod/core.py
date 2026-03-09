
#Launch Command Spawner : LCS => LCS mod
import minecraft_launcher_lib, subprocess, random
import psutil
import os
import zipfile
import json
from PIL import Image
import platform
import sys
import time

#downloader
import requests as req
from tqdm import tqdm

#加密

import base64
import pathlib

#生成一些先秦時代的魔法語言
import secrets

import traceback

#尋找並指派電腦上的 .minecraft 資料夾給 minecraft_directory 變數
try:
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
    print(f"找到 Minecraft 資料夾：{minecraft_directory}")
except minecraft_launcher_lib.utils.MinecraftDirectoryNotFound:
    print("未找到 Minecraft 資料夾，請確保已安裝 Minecraft Launcher")
    sys.exit(1)

total_memory_mb= int(tuple(psutil.virtual_memory())[0] / (1024 * 1024))  # 總記憶體大小（MB）
print(f"總記憶體大小：{total_memory_mb} MB")

home_path=f"{pathlib.Path.home()}" + "\\Desktop\\" #取得Desktop資料夾的位置
print(f"桌面路徑：{home_path}")

def system_check():
    if platform.system() == "Windows":
        win_ver = sys.getwindowsversion()
        if win_ver.build >= 22000:
            print("這是 Windows 11")
            
            is_bedrock_launch=True
        elif win_ver.build >= 10240:   
            print("這是 Windows 10")
            is_bedrock_launch=True 
        else:
            print("這是更早版本的 Windows")
            is_bedrock_launch=False
    else:
        print(f"這不是Windows系統，這是{platform.system()}")
        is_bedrock_launch=False

    return is_bedrock_launch
#檢查系統是否為 Windows 11 或 Windows 10

#online_ver_list = minecraft_launcher_lib.utils.get_available_versions(minecraft_directory)

#迫於寫成module的需要，指定一個別
class Launcher:
    @staticmethod
    def normal(ver: str, wide: int = 800, high: int = 600, 
               username: str = f"player{random.randrange(100,1000)}", 
               executablePath: str = None, 
               memory:int = 1536, kib:str = "M", 
               server: str = None, port: int = None, 
               jvm_argv: list = None, 
               full_screen: bool = False):
        global options
        t = {"username": "The Username", "uuid": "The UUID", "token": "The access token"}
        options = minecraft_launcher_lib.utils.generate_test_options()
        options["resolutionWidth"] = str(wide)
        options["resolutionHeight"] = str(high)
        options["gameDirectory"] = minecraft_directory
        options["launcherName"]="UMCL by Cookie"
        if executablePath == None or executablePath == "":
            options["executablePath"]=minecraft_launcher_lib.utils.get_java_executable()
        else:
            options["executablePath"]=executablePath
        options["jvmArguments"]=[f"-Xmx{memory}{kib}"]
        if jvm_argv:
            options["jvmArguments"].extend(jvm_argv)
        if full_screen == True:
            options["jvmArguments"].extend(["-Dorg.lwjgl.opengl.Window.undecorated=true"])
        options["username"] = str(username)
        options["token"] = secrets.token_urlsafe(10)
        if server is not None and port is not None:
            options["server"] = server 
            options["port"] = port 
        options["uuid"] = secrets.token_urlsafe(10)
        options["accessToken"] = secrets.token_urlsafe(10)
        #以下是偵測版本正不正確，如本地沒有此版本就抱錯

        try:
            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(ver, minecraft_directory, options)
            
            #把list 轉成 文字
            """
            with open("launch_cmd_temp.bat","w") as f:
                f.write("javaw ")
            long=len(minecraft_command)
            times=0
            for i in minecraft_command:
                times += 1
                if (times == 1) == False:
        
                    with open("launch_cmd_temp.bat","a") as f:
        
                        f.write(i)
                        if (times == long) == False:
                            f.write(" ")
                            """

                            
            return minecraft_command
            
            


        except Exception as e:
            traceback.print_exc()
            print(f"Launch error: {e}")
#這部份給我自己debug的
    def normal_debug(debug):
        if debug == "mcdir":
            return minecraft_directory
        elif debug == "opt":
            return options
    def get_local_ver(give=None):
        global local_ver_list
        local_ver_list=[]
        try:
            for i in minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory):
                local_ver_list.append(i["id"])
            
        except Exception as e:
            print(f"ERROR {e}")
        return local_ver_list
    def analyze_resourcepack(path: str) -> dict:
        """
        分析一個 Minecraft 材質包（.zip 或資料夾）

        參數:
            path: str - 材質包路徑（可以是資料夾或 .zip）

        回傳 dict:
            {
                "valid": True/False,
                "pack_format": int or None,
                "description": str or None,
                "icon": PIL.Image 或 None,
                "error": str 或 None
            }
        """
        result = {
            "valid": False,
            "pack_format": None,
            "description": None,
            "icon": None,
            "error": None
        }

        try:
            # 判斷資料類型
            if os.path.isdir(path):
                entries = os.listdir(path)
                open_file = lambda name: open(os.path.join(path, name), "r", encoding="utf-8").read()
                open_image = lambda name: Image.open(os.path.join(path, name))
            elif zipfile.is_zipfile(path):
                z = zipfile.ZipFile(path, 'r')
                entries = z.namelist()
                open_file = lambda name: z.read(name).decode("utf-8")
                open_image = lambda name: Image.open(z.open(name))
            else:
                result["error"] = "不是合法的 zip 或資料夾"
                return result

            # pack.mcmeta 分析
            meta_name = next((f for f in entries if f.endswith("pack.mcmeta")), None)
            if not meta_name:
                result["error"] = "找不到 pack.mcmeta"
                return result

            mcmeta_data = open_file(meta_name)
            meta = json.loads(mcmeta_data)
            result["pack_format"] = meta.get("pack", {}).get("pack_format")
            result["description"] = meta.get("pack", {}).get("description")
            result["valid"] = True

        # 嘗試載入 pack.png
            icon_name = next((f for f in entries if f.endswith("pack.png")), None)
            if icon_name:
                result["icon"] = open_image(icon_name)

        except Exception as e:
            result["error"] = str(e)

        return result

    def suggest_mc_version(pack_format: int) -> str:
        format_map = {
            1: "1.6 – 1.8.9",
            2: "1.9 – 1.10.2",
            3: "1.11 – 1.12.2",
            4: "1.13 – 1.14.4",
            5: "1.15 – 1.16.1",
            6: "1.16.2 – 1.16.5",
            7: "1.17",
            8: "1.18 – 1.18.2",
            9: "1.19 – 1.19.2",
            10: "1.19.3",
            11: "1.19.4",
            12: "1.20 – 1.20.1",
            13: "1.20.2",
            14: "1.20.3 – 1.20.4",
            15: "1.20.5+"
        }
        return format_map.get(pack_format, "未知版本（可能為未來或錯誤）")
    
    def install_game(ver: str, Callback=None):
        minecraft_launcher_lib.install.install_minecraft_version(ver, minecraft_directory, callback=Callback)


class other_function:
    
    
    def game_config(mode, data=None):
        if mode == "save":
            with open("app_config/game_config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return "配置已保存"
        elif mode == "load":
            try:
                with open("app_config/game_config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(data)
                    return data
            except FileNotFoundError:
                return None
        else:
            raise ValueError("無效的模式，請使用 'save' 或 'load'")
        
        
 


    def get_all_java_listen_ports():
        java_ports = []
    
        # 遍歷所有進程
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 鎖定 Java 相關進程
                if 'java' in proc.info['name'].lower() or 'javaw' in proc.info['name'].lower():
                    connections = proc.connections(kind='tcp')
                    for conn in connections:
                        # 只找正在監聽 (LISTEN) 的連線
                        if conn.status == psutil.CONN_LISTEN:
                            port = conn.laddr.port
                            # 排除掉一些常見的系統保留或已知非遊戲 Port (可選)
                            # 例如 5005 是常用的 Java Debug Port
                            if port not in java_ports:
                                java_ports.append(port)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            
        # 由小到大排序，方便前端顯示
        return sorted(java_ports)
    
    def start_ngrok_tunnel(port):
        # 1. 在背景啟動 ngrok (使用 subprocess.Popen 避免卡住主程式)
        # 確保你已經把 ngrok.exe 放進專案目錄或加入環境變數
        print(f"正在啟動 ngrok 隧道，監聽本地端口 {port}...")
        cmd = ["ngrok", "tcp", str(port)]
    
        # creationflags=0x08000000 是 Windows 專屬：完全不顯示黑框
        subprocess.Popen(cmd, creationflags=0x08000000)
        
        for i in range(10):  # 最多檢查 10 次，每次間隔 2 秒
            time.sleep(2)  # 每秒檢查一次 ngrok 是否已經啟動並提供網址
            try:
                response = req.get("http://127.0.0.1:4040/api/tunnels")
                if response.status_code == 200:
                    data = response.json()
        
                    # 4. 解析 JSON 拿到公網地址
                    # data['tunnels'][0]['public_url'] 通常長這樣: "tcp://0.tcp.jp.ngrok.io:12345"
                    public_url = data['tunnels'][0]['public_url']
        
                    # 去掉 tcp:// 字頭，方便玩家直接複製
                    clean_url = public_url.replace("tcp://", "")
        
                    return clean_url
                elif response.status_code == 404:
                    print("ngrok API 尚未啟動，繼續等待...")
                    continue
            except Exception as e:
                traceback.print_exc()
                print(f"無法抓取 ngrok 網址: {e}")
                break
        return None
    
        

    
    
   




