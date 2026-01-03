from tqdm import tqdm
import time
from tqdm import tqdm
import time

with tqdm(total=100, 
          bar_format='{desc}: {n_fmt}/{total_fmt} |{bar}| after:{elapsed} | time left:{remaining}, {rate_fmt}', 
          desc="處理中") as pbar:
    for i in range(100):
        time.sleep(0.5)
        pbar.update(1)  # 每次更新進度條 10%
    pbar.set_description("完成")