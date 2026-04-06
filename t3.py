from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import Frame, Label
from prompt_toolkit.formatted_text import HTML

items = ["🚀 開始新遊戲", "⚙️  設定", "📖 說明", "❌ 離開"]
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
    event.app.exit(result=-1)

layout = Layout(Frame(HSplit([label]), title="主選單"))
app = Application(layout=layout, key_bindings=kb, full_screen=True)
result = app.run()
print(f"你選了：{items[result]}")