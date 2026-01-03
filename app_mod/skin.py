from PIL import Image, ImageTk
import io
import base64
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

def get_face_image(skin_path, scale=8, include_hat=True):
    """
    從皮膚產生放大的臉部 PIL.Image（RGBA）。

    :param skin_path: 皮膚檔案路徑
    :param scale: 放大倍率，預設 8
    :param include_hat: 是否包含帽子層
    :return: PIL.Image (RGBA)
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

    # 放大並以 NEAREST 保持像素風格
    face_big = face.resize((8 * scale, 8 * scale), Image.NEAREST)
    return face_big


def show_minecraft_face(skin_path, scale=8, include_hat=True):
    """
    在 Tkinter 視窗中顯示 Minecraft 皮膚的臉部，回傳 `ImageTk.PhotoImage`（向後相容）。
    """
    face_big = get_face_image(skin_path, scale, include_hat)
    tk_image = ImageTk.PhotoImage(face_big)
    return tk_image


def show_minecraft_face_html(skin_path, scale=8, include_hat=True, as_data_uri=True, save_path=None):
    """
    產生可在 HTML 使用的臉部圖片。

    回傳值行為說明：
      - 若 `save_path` 為 None，且 `as_data_uri` 為 True：回傳 data URI 字串 'data:image/png;base64,...'
      - 若 `save_path` 提供，且 `as_data_uri` 為 True：會先儲存檔案，回傳 (data_uri, save_path)
      - 若 `as_data_uri` 為 False 且 `save_path` 提供：儲存檔案並回傳檔案路徑
      - 若 `as_data_uri` 為 False 且 `save_path` 為 None：回傳 PNG 二進位資料（bytes）

    :param skin_path: 皮膚路徑
    :param scale: 放大倍率
    :param include_hat: 是否包含帽子層
    :param as_data_uri: 是否回傳 data URI（預設 True）
    :param save_path: 若提供則同時儲存 PNG 到該路徑
    """
    face_big = get_face_image(skin_path, scale, include_hat)

    buffer = io.BytesIO()
    face_big.save(buffer, format='PNG')
    data = buffer.getvalue()

    if save_path:
        with open(save_path, 'wb') as f:
            f.write(data)

    if as_data_uri:
        encoded = base64.b64encode(data).decode('ascii')
        data_uri = f"data:image/png;base64,{encoded}"
        return (data_uri, save_path) if save_path else data_uri
    else:
        return save_path if save_path else data

# 🚀 範例用法
if __name__ == "__main__":
    skin = "user_data/skin.png"  # 可以是 JPG/BMP/PNG
    valid, model, final = mojang_skin_checker(skin)
    print("結果:", "有效" if valid else "無效", "| 模型:", model, "| 最終檔案:", final)

    if valid and final:
        # 產生 HTML data URI（可直接放到 <img src="...">）
        data_uri = show_minecraft_face_html(final)
        print("data URI 範例（前 120 字）：", data_uri[:120], "...")

        # 同時儲存成檔案並回傳路徑
        saved_path = show_minecraft_face_html(final, as_data_uri=False, save_path="user_data/face.png")
        print("已儲存到：", saved_path)
