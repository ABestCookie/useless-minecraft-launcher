# pip install textual
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem, Label
from textual.binding import Binding

class MyApp(App):
    CSS = """
    Screen { background: #000080; }
    ListView { border: solid white; background: #000080; }
    ListItem.--highlight { background: #aaaaaa; color: #000080; }
    """

    BINDINGS = [
        Binding("q", "quit", "離開"),
        Binding("f1", "help", "說明"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()          # 自動產生頂部標題列
        yield ListView(
            ListItem(Label("開始新遊戲")),
            ListItem(Label("載入存檔")),
            ListItem(Label("設定")),
            ListItem(Label("離開")),
        )
        yield Footer()          # 自動產生底部快捷鍵列

app = MyApp()
app.run()