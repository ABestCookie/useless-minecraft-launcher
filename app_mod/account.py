# ===== Minecraft啟動器帳號管理模組 =====
# 此模組負責管理玩家帳號信息，包括帳號的新增、讀取、更新和刪除等操作

import json, logging  # json用於讀寫帳號數據文件，logging用於記錄程式運行日誌
if __name__ == "__main__":
    from skin import mojang_skin_checker  # 直接運行此文件時，從同目錄導入皮膚檢查函數
else:
    from app_mod.skin import mojang_skin_checker  # 被其他模組引入時，從app_mod包導入皮膚檢查函數
import secrets  # 用於生成隨機的皮膚文件名
import os  # 用於操作系統相關操作

# ===== 設定日誌記錄 =====
logging.basicConfig(
    level=logging.DEBUG,  # 設定最低輸出等級為DEBUG（會記錄所有等級的消息）
    filename="debug.log",  # 日誌文件名
    filemode="a",  # "a"表示追加模式（不覆蓋舊日誌），"w"表示覆蓋模式
    format="%(asctime)s [%(levelname)s] %(message)s"  # 日誌格式：時間 [日誌等級] 消息
)

# ===== 讀取帳號信息函數 =====
def read(username=None):
    """
    讀取帳號信息
    
    參數:
        username: 要讀取的帳號名稱。如果為None或空字符串，則列出所有帳號
    
    返回:
        如果有指定帳號名：返回該帳號的詳細信息（字典）
        如果沒指定帳號名：返回所有帳號的字典（鍵為帳號名，值為帳號詳細信息）
        如果帳號不存在或文件不存在：返回空字典 {}
    """
    # 修正：預設 list_accounts 為 False（只有在username為None/空時才設為True）
    list_accounts = False
    if username is None or username == "" or not username:
        # 用戶沒有指定帳號名，所以要列出所有帳號
        logging.info("List all accounts.")
        list_accounts = True
    try:
        # 打開帳號數據文件（JSON格式）
        with open("user_data/account.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if list_accounts:
                # 列出所有帳號 - 返回整個字典而不是只返回名稱列表
                logging.info("Listing all accounts:")
                count = len(data)  # 帳號計數
                logging.info(f"Total accounts: {count}")
                return data  # 直接返回整個帳號字典
            else:
                # 返回指定帳號的信息
                try:
                    return data[username]
                except KeyError:
                    # 帳號不存在時的錯誤處理
                    logging.error(f"Account '{username}' not found.")
                    return {}
    except FileNotFoundError:
        # 帳號文件不存在時的錯誤處理
        logging.error("Account file not found. Please create an account first.")
        return {}



# ===== 寫入（創建/更新）帳號信息函數 =====
def write(name, account_type, skin: str=None):
    """
    創建或更新玩家帳號
    
    參數:
        name: 帳號名稱
        account_type: 帳號類型（目前只支持"offline"離線帳號）
        skin: 皮膚文件路徑（可選）
    
    返回:
        成功時：無返回值（None）
        失敗時：返回錯誤代碼
        - "E01": 帳號已存在
        - "E02": 皮膚文件無效
    """
    
    # ===== 第一部分：檢查帳號文件和判斷寫入模式 =====
    try:
        # 打開現有的帳號文件
        with open("user_data/account.json", "r", encoding="utf-8") as r:
            data = json.load(r)
            if not data or data == {}:
                # 帳號文件為空，需要用寫入模式（會創建新文件）
                mode_type = "w"
                logging.warning("Account file is empty, creating a new one.")
            elif name in data:
                # 帳號已存在，返回錯誤代碼E01
                mode_type = "w"
                logging.warning(f"Account '{name}' already exists, overwriting.")
                return "E01"  # E01: Account already exists
            else:
                # 帳號不存在，可以追加新帳號
                mode_type = "a"
    except FileNotFoundError:
        # 帳號文件不存在，需要創建新文件
        mode_type = "w"
        data = {}
    
    # ===== 第二部分：處理皮膚文件 =====
    if skin is not None:
        # 用戶提供了皮膚文件
        valid, model, final = mojang_skin_checker(skin)  # 驗證皮膚文件是否有效
        if valid == False:
            # 皮膚文件無效
            logging.error("Failed to load skin. Please check the skin file.")
            image_road = r"art/steve.png"  # 使用默認皮膚（Steve）
            model = "Steve"
            return "E02"  # E02: Invalid skin file
        else:
            # 皮膚文件有效
            logging.info(f"Skin '{skin}' is valid. Model type: {model}. Final path: {final}")
            # 生成隨機文件名來保存皮膚圖片（避免命名衝突）
            image_road=f"user_data/{str(secrets.token_urlsafe(8))}.png"
            # 複製皮膚文件到user_data目錄
            with open(final, "rb") as f:
                with open(image_road, "wb") as f2:
                    f2.write(f.read())
    elif skin is None:
        # 用戶沒有提供皮膚文件，使用默認Steve皮膚
        logging.info("No skin provided, using default skin.")
        image_road = r"art/steve.png"
        model = "Steve"

    # ===== 第三部分：構建帳號數據 =====
    difault_data={
                        (name): {  # 帳號名稱作為鍵
                            "user_name": name,  # 玩家名稱
                            "account_type": account_type,  # 帳號類型（offline/online）
                            #以下因為是離線帳號，所以這些信息可以是隨機值
                            "uuid": "*random*",  # UUID：用於識別玩家的唯一ID（離線帳號用隨機值）
                            "token": "*random*",  # 令牌：用於登錄驗證（離線帳號用隨機值）
                            "access_token": "*random*",  # 訪問令牌（離線帳號用隨機值）
                            "client_token": "*empty*",  # 客戶端令牌（離線帳號不需要）
                            "skin": {"model": model, "path": image_road if skin else None}   # 皮膚信息
                    }
                }

    # ===== 第四部分：寫入帳號數據到文件 =====
    try:
        with open("user_data/account.json", mode_type, encoding="utf-8") as f:
            if mode_type == "a":
                # 追加模式：在現有帳號基礎上添加新帳號
                with open("user_data/account.json", "r", encoding="utf-8") as r:
                    data= json.load(r)
                if not data or data == {}:
                    logging.error("Account data is empty. Cannot update. Please create an account first.")
                    return
                data[name] = difault_data[name]  # 將新帳號數據添加到現有數據中
                with open("user_data/account.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                logging.info(f"Account '{name}' create successfully.")
            else:
                # 寫入模式：創建新的帳號文件
                if account_type == "offline":
                    # 離線帳號創建
                    json.dump(difault_data, f, indent=4)
                    logging.info(f"Offline account '{name}' create successfully.")
                else:
                    # 不支持的帳號類型
                    logging.error(f"Unknown account type: {account_type}. Please use 'offline' for offline accounts.")
                    if account_type == "online":
                        logging.warning("Online account creation is not supported in this version.")
                    return
    except FileNotFoundError:
        # 帳號文件不存在時的錯誤處理
        logging.error("Account file not found. Please create an account first.")
        return


# ===== 刪除帳號函數 =====
def delete(username):
    """
    刪除指定的玩家帳號
    
    參數:
        username: 要刪除的帳號名稱
    
    返回:
        成功時：無返回值（None）
        失敗時：返回錯誤代碼
        - "F01": 文件不存在
    """
    try:
        # 打開帳號文件
        with open("user_data/account.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if username in data:
                # 找到要刪除的帳號，從字典中刪除
                del data[username]
                # 將修改後的數據重新寫入文件
                with open("user_data/account.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                logging.info(f"Account '{username}' deleted successfully.")
            else:
                # 要刪除的帳號不存在
                logging.error(f"Account '{username}' not found.")
    except FileNotFoundError:
        # 帳號文件不存在
        logging.error("Account file not found. Please create an account first.")
        return "F01"  # F01: File not found

# ===== 測試代碼 =====
if __name__ == "__main__":
    # 這段代碼只在直接運行此文件時才會執行
    # 用於測試帳號創建功能
    os.chdir("C:\\Users\\Yachi\\Desktop\\useless minecraft launcher")
    # 創建一個名為"WafflyBat"的離線帳號，並使用指定的皮膚文件
    write("WafflyBat", "offline", "create", "user_data/skin.png")