import sys
import os
import subprocess
import json
import tqdm
import traceback
import requests as req

def download(url):
    try:
        # 1. 取得文件總大小
        size_in_bytes, size_in_mb = get_file_size(url)
        if size_in_bytes is not None:
            print(f"文件大小: {size_in_bytes} bytes ({size_in_mb:.2f} MB)")
        else:
            print("伺服器未提供文件大小資訊，將不顯示進度百分比")
    except Exception as e:
        print(f"預檢失敗: {e}")
        size_in_bytes = None

    filename = url.split('/')[-1]
    
    # 2. 開始串流下載
    r = req.get(url, stream=True)
    
    # 3. 設定 tqdm 進度條
    # unit='B', unit_scale=True 會自動轉換單位（如 KB, MB）
    progress_bar = tqdm.tqdm(
        total=size_in_bytes, 
        unit='B', 
        unit_scale=True, 
        desc=f"正在下載 {filename}"
    )

    with open(filename, 'wb') as f:
        for data in r.iter_content(chunk_size=1024):
            f.write(data)
            # 4. 手動更新進度條，每次增加實際讀取的數據長度
            progress_bar.update(len(data))
            
    progress_bar.close()
    return filename

def get_file_size(url):
    # 發送 HEAD 請求來檢查文件資訊
        response = req.head(url)
    
        if response.status_code == 200:  # 確保請求成功
            content_length = response.headers.get('Content-Length')
            if content_length is not None:
                size_in_bytes = int(content_length)
                size_in_mb = size_in_bytes / (1024 * 1024)  # 將位元組轉換為 MB
                return size_in_bytes, size_in_mb
            else:
                return None, None  # 沒有 Content-Length 標頭
        else:
            raise Exception(f"無法檢查文件大小，HTTP 狀態碼：{response.status_code}")
    
if __name__ == "__main__":
    url = "https://launcher.mojang.com/download/MinecraftInstaller.exe"
    try:
        downloaded_file = download(url)
        print(f"文件已成功下載：{downloaded_file}")
    except Exception as e:
        traceback.print_exc()  # 打印完整的錯誤堆棧信息到控制台
        print(f"下載失敗：{e}")