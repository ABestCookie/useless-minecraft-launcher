import json, logging
if __name__ == "__main__":
    from skin import mojang_skin_checker
else:
    from app_mod.skin import mojang_skin_checker
import secrets
import os
logging.basicConfig(
    level=logging.DEBUG,  # 設定最低輸出等級
    filename="debug.log",
    filemode="a",  # 覆蓋用 "w"，追加用 "a"
    format="%(asctime)s [%(levelname)s] %(message)s"
)
def read(username=None):
    # 修正：預設 list_accounts 為 False
    list_accounts = False
    if username is None or username == "" or not username:
        logging.info("List all accounts.")
        list_accounts = True
    try:
        with open("user_data/account.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if list_accounts:
                logging.info("Listing all accounts:")
                displayname = []
                count = 0
                for i in data:
                    displayname.append(i)
                    count += 1
                logging.info(f"Total accounts: {count}")
                return displayname
            else:
                try:
                    return data[username]
                except KeyError:
                    logging.error(f"Account '{username}' not found.")
                    return {}
    except FileNotFoundError:
        logging.error("Account file not found. Please create an account first.")
        return {}

def write(name, account_type, skin: str=None):
    
    try:
        with open("user_data/account.json", "r", encoding="utf-8") as r:
            data = json.load(r)
            if not data or data == {}:
                mode_type = "w"
                logging.warning("Account file is empty, creating a new one.")
            elif name in data:
                mode_type = "w"
                logging.warning(f"Account '{name}' already exists, overwriting.")
                return "E01"  # E01: Account already exists
            else:
                mode_type = "a"
    except FileNotFoundError:
        mode_type = "w"
        data = {}
    
    if skin is not None:
        valid, model, final = mojang_skin_checker(skin)
        if valid == False:
            logging.error("Failed to load skin. Please check the skin file.")
            image_road = r"art/steve.png"
            model = "Steve"
            return "E02"  # E02: Invalid skin file
        else:
            logging.info(f"Skin '{skin}' is valid. Model type: {model}. Final path: {final}")
            image_road=f"user_data/{str(secrets.token_urlsafe(8))}.png"
            with open(final, "rb") as f:
                with open(image_road, "wb") as f2:
                    f2.write(f.read())
    elif skin is None:
        logging.info("No skin provided, using default skin.")
        image_road = r"art/steve.png"
        model = "Steve"

    
    difault_data={
                        (name): {
                            "user_name": name,
                            "account_type": account_type,
                            #以下因為是離線帳號，所以這些資訊不需要
                            "uuid": "*random*",
                            "token": "*random*",
                            "access_token": "*random*",
                            "client_token": "*empty*",
                            "skin": {"model": model, "path": image_road if skin else None}   
                    }
                }

    try:
        with open("user_data/account.json", mode_type, encoding="utf-8") as f:
            if mode_type == "a":
                with open("user_data/account.json", "r", encoding="utf-8") as r:
                    data= json.load(r)
                if not data or data == {}:
                    logging.error("Account data is empty. Cannot update. Please create an account first.")
                    return
                data[name] = difault_data
                json.dump(data, f, indent=4)
                logging.info(f"Account '{name}' create successfully.")
            else:
                if account_type == "offline":
                    
                    json.dump(difault_data, f, indent=4)

                    logging.info(f"Offline account '{name}' create successfully.")
                else:
                    logging.error(f"Unknown account type: {account_type}. Please use 'offline' for offline accounts.")
                    if account_type == "online":
                        logging.warning("Online account creation is not supported in this version.")
                    return
    except FileNotFoundError:
        logging.error("Account file not found. Please create an account first.")
        return
    
def delete(username):
    try:
        with open("user_data/account.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            if username in data:
                del data[username]
                with open("user_data/account.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                logging.info(f"Account '{username}' deleted successfully.")
            else:
                logging.error(f"Account '{username}' not found.")
    except FileNotFoundError:
        logging.error("Account file not found. Please create an account first.")
        return "F01"  # F01: File not found
if __name__ == "__main__":
    os.chdir("C:\\Users\\Yachi\\Desktop\\useless minecraft launcher")
    write("WafflyBat", "offline", "create", "user_data/skin.png")