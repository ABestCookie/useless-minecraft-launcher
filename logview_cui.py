from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, ScrollablePane, HSplit
from prompt_toolkit.widgets import Frame, Label
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import radiolist_dialog, message_dialog, input_dialog

import os
import gzip
import sys
import subprocess
import json


def selecte_list(items, Title):

    selected = [0]   # 用 list 讓 closure 能修改

    def get_content():
        lines = []
        for i, item in enumerate(items):
            if i == selected[0]:
                lines.append(f'<b><style bg="ansicyan"> ▶ {item} </style></b>')
            else:
                lines.append(f'   {item}')
        return HTML("\n".join(lines))

    label = Label(text=get_content)

    kb = KeyBindings()

    @kb.add("up")
    def _up(event):
        selected[0] = (selected[0] - 1) % len(items)

    @kb.add("down")
    def _down(event):
        selected[0] = (selected[0] + 1) % len(items)

    @kb.add("enter")
    def _enter(event):
        event.app.exit(result=selected[0])

    @kb.add("q")
    def _quit(event):
        sys.exit(0)

    # ScrollablePane 自動處理捲動
    layout = Layout(
        Frame(
            ScrollablePane(HSplit([label])),  # 包一層就好
            title=Title,
            height=15        # 視窗固定高度，超出自動捲
        )
    )
    app = Application(layout=layout, key_bindings=kb, full_screen=True)
    result = app.run()
    print(f"你選了：{items[result]}")
    return result
    
if __name__ == "__main__":
    while True:
        callback = selecte_list(items=["ℹ️  查看日誌", "⚙️  設定", "📖 說明", "❌ 離開"], Title="主選單")
        if callback == 0:
            get_log_list = os.listdir("logs")
            item_list = []
            for i in get_log_list:
                item_list.append((i, i))
            result = radiolist_dialog(
                title="日誌列表",
                text="請用方向鍵選擇，Enter確認：",
                values=item_list,
            ).run()
            if result is not None:
                with open("app_config/log_viewer_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                print(f"你選了：{result}")
                if result.endswith(".log.gz"):
                    with gzip.open(f"logs/{result}", 'rt', encoding='utf-8') as f:
                        content = f.read()
                        with open(f"logs/temp", 'w', encoding='utf-8') as out:
                            out.write(content)
                    try:
                        subprocess.run([config["viewer"], "-M", f"logs/temp"])
                    except Exception as e:
                        message_dialog(
                            title="錯誤",
                            text=f"無法開啟日誌：{e}"
                        ).run()
                    os.remove(f"logs/temp")
                else:
                    try:
                        subprocess.run([config["viewer"], "-M", f"logs/{result}"])
                    except Exception as e:
                        message_dialog(
                            title="錯誤",
                            text=f"無法開啟日誌：{e}"
                        ).run()
        elif callback == 1:
            result = radiolist_dialog(
                title="設定",
                text="請用方向鍵選擇，Enter確認：",
                values=[("viewer", "日誌查看器(預設為vim)"), 
                        ("language", "語言")]
            ).run()
            if result == "viewer":
                result_path = input_dialog(
                    title="自訂日誌查看器",
                    text="請輸入完整路徑："
                ).run()
            elif result == "language":
                message_dialog(
                    title="語言設定",
                    text="目前僅支援中文，未來可能會加入其他語言。"
                ).run()
            try:
                with open("app_config/log_viewer_config.json", "w", encoding="utf-8") as f:
                    data = {}
                    data["viewer"] = result_path
                    json.dump(data, f, ensure_ascii=False, indent=4)
                message_dialog(
                    title="成功",
                    text="設定已儲存！"
                ).run()
            except Exception as e:
                message_dialog(
                    title="錯誤",
                    text=f"無法儲存設定：{e}"
                ).run()
        elif callback == 2:
            message_dialog(
                title="說明",
                text="日誌查看工具，一個因為我不想寫html而誕生的東西🙃，用 prompt_toolkit 實現。\n\n- 使用上下鍵選擇選項，Enter確認。\n- 在日誌列表中選擇日誌文件，會使用 Vim 打開。\n- 支持 .log 和 .log.gz 格式的日誌文件。",
            ).run()
        elif callback == 3:
            sys.exit(0)
    