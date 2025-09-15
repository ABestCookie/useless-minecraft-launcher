from PIL import Image, ImageTk
import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    filename="debug.log",
    filemode="a",  # 覆蓋用 "w"，追加用 "a"  # 設定最低輸出等級
    format="%(asctime)s [%(levelname)s] %(message)s"
)
def mojang_skin_checker(skin_path: str):
    """
    檢查 Minecraft skin 是否符合 Mojang 標準，並判斷是 Steve 還是 Alex。
    如果不是 PNG 格式，自動轉換為 PNG。
    
    :param skin_path: 皮膚檔案路徑
    :return: (is_valid, model_type, final_path)
             is_valid: True/False
             model_type: "Steve" / "Alex" / None
             final_path: 最終檔案路徑
    """
    if not os.path.isfile(skin_path):
        logging.error(f"❌ 檔案不存在：{skin_path}")
        return False, None, None

    try:
        img = Image.open(skin_path)
    except Exception as e:
        logging.error(f"❌ 無法打開圖片: {e}")
        return False, None, None

    final_path = skin_path

    # 如果不是 PNG，自動轉換
    if img.format != "PNG":
        final_path = os.path.splitext(skin_path)[0] + "_converted.png"
        img = img.convert("RGBA")
        img.save(final_path, "PNG")
        
        logging.warning(f"ℹ️ 圖片不是 PNG，已轉換並儲存為: {final_path}")
    else:
        img = img.convert("RGBA")

    # 檢查尺寸
    width, height = img.size
    if (width, height) not in [(64, 32), (64, 64)]:
        logging.error(f"❌ 尺寸錯誤: {width}x{height} 不是 64x32 或 64x64")
        return False, None, final_path

    
    logging.info(f"✅ 格式與尺寸檢查通過: {width}x{height} PNG")

    # 如果是 64x32 沒有 Alex 模型
    if (width, height) == (64, 32):
        logging.warning(f"ℹ️ 舊版皮膚，只支援 Steve")
        return True, "Steve", final_path

    # 判斷 Alex 還是 Steve
    alex_area = [(54, y) for y in range(20, 32)]
    is_alex = True
    for x, y in alex_area:
        pixel = img.getpixel((x, y))
        if pixel[3] != 0:
            is_alex = False
            break

    model_type = "Alex" if is_alex else "Steve"
    logging.info(f"✅ 模型判定: {model_type}")

    return True, model_type, final_path

def show_minecraft_face(skin_path, scale=8, include_hat=True):
    """
    在 Tkinter 視窗中顯示 Minecraft 皮膚的臉部。
    
    :param skin_path: 皮膚檔案路徑
    :param scale: 放大倍率，默認 8 倍
    :param include_hat: 是否包含帽子層
    """
    skin = Image.open(skin_path).convert("RGBA")

    # 裁剪臉部 (8,8)-(15,15)
    face_box = (8, 8, 16, 16)
    face = skin.crop(face_box)

    if include_hat:
        # 裁剪帽子層 (40,8)-(47,15)
        hat_box = (40, 8, 48, 16)
        hat = skin.crop(hat_box)

        # 合併臉和帽子
        face = Image.alpha_composite(face, hat)

    # 放大
    face_big = face.resize((8 * scale, 8 * scale), Image.NEAREST)

    # 轉換成 Tkinter 圖像
    tk_image = ImageTk.PhotoImage(face_big)
    
    return tk_image

# 🚀 範例用法
if __name__ == "__main__":
    skin = "user_data/skin.png"  # 可以是 JPG/BMP/PNG
    valid, model, final = mojang_skin_checker(skin)
    print("結果:", "有效" if valid else "無效", "| 模型:", model, "| 最終檔案:", final)
