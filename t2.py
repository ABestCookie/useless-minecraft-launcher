from prompt_toolkit.shortcuts import radiolist_dialog

items = [(f"item_{i}", f"選項 {i+1}") for i in range(30)]
print(items)

result = radiolist_dialog(
    title="主選單",
    text="請用方向鍵選擇，Enter確認：",
    values=items,
).run()

print(f"選了：{result}")