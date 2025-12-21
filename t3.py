import subprocess

def run_command(command):
    # 使用 Popen 啟動進程
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # 將錯誤輸出也合併到標準輸出
        text=True,                 # 自動解碼為字串
        bufsize=1                  # 行緩衝
    )

    # 即時循環讀取每一行
    for line in process.stdout:
        print(f"捕捉到日誌: {line.strip()}") 
        # 在這裡可以進行日誌寫入文件、GUI 更新或條件判斷

    # 等待進程結束並獲取回傳碼
    return_code = process.wait()
    print(f"進程結束，回傳碼: {return_code}")

# 範例：執行一個會持續輸出的指令
run_command(["ping", "google.com", "-n", "5"])  # Windows 範例，Linux/Mac 可改為 ["ping", "-c", "5", "google.com"]
