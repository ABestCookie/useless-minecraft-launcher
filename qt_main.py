# Minecraft_Launcher_PyQt5_Full.py

import os
import sys
import json
import pathlib
import subprocess
import threading
import datetime
import platform

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLabel, QComboBox, QCheckBox,
    QVBoxLayout, QProgressBar, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
    QTextEdit, QDialog, QScrollArea, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import minecraft_launcher_lib
import app_mod.core as core
import numba

width = 800
height = 600
home_path = f"{pathlib.Path.home()}\\Desktop\\"
minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
current_max = 0
web_fullscreen = False

# 讀取設定檔
try:
    with open("user_data/common.json", "r") as r:
        common_option = json.loads(r.read())
except:
    with open("user_data/common.json", "w") as w:
        data = {"toggle": False, "ver": None}
        json.dump(data, w, indent=2)
        common_option = data

callback = {
    "setStatus": lambda status: set_status(status),
    "setProgress": lambda progress: set_progress(progress),
    "setMax": lambda m: set_max(m)
}


@numba.jit(nogil=True, cache=True)
def check_minecraft_log(text: str) -> dict:
    text_lower = text.lower()
    分類關鍵詞 = {
        "正常": ["stopping server", "shutting down", "saving chunks", "saving worlds", "goodbye"],
        "異常": ["exception", "stacktrace", "crash", "error", "exit code", "java.lang", "caused by", "traceback", "fatal", "panic"],
        "啟動失敗": ["launching failed", "failed to launch", "invalid version", "missing", "could not find", "launchwrapper", "launch error"]
    }
    for 狀態, 關鍵字列表 in 分類關鍵詞.items():
        for kw in 關鍵字列表:
            if kw in text_lower:
                for line in text.splitlines():
                    if kw in line.lower():
                        return {"狀態": 狀態, "關鍵詞": line.strip()}
    return {"狀態": "不明", "關鍵詞": "未偵測到明確結束訊息"}


def install_in_thread(version: str):
    def run_install():
        set_status(f"準備安裝 Minecraft {version}")
        minecraft_launcher_lib.install.install_minecraft_version(
            version, minecraft_directory, callback=callback
        )
        set_status("✔ 安裝完成")
        set_max(0)
        threading.Thread(target=run_game_from_batch, daemon=True).start()

    threading.Thread(target=run_install, daemon=True).start()


def run_game_from_batch():
    try:
        bat_path = os.path.join(os.getcwd(), "launch_cmd_temp.bat")
        process = subprocess.Popen(
            ["cmd.exe", "/c", bat_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=os.getcwd()
        )
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
        process.wait()
        full_output = "".join(output_lines)
        analyze_and_show_log(full_output)
    except Exception as e:
        print("❌ 執行 bat 發生錯誤：", e)
        analyze_and_show_log(f"啟動失敗：{e}")


def set_status(status: str):
    print(f"[狀態] {status}")
    if "task_label" in globals():
        task_label.setText(f"任務：{status.strip()}")
        task_label.setVisible(True)


def set_progress(progress: int):
    if current_max != 0:
        percent = int(progress / current_max * 100)
        if "bar" in globals():
            bar.setValue(percent)
        if "progress_label" in globals():
            progress_label.setText(f"安裝進度：{percent}%")


def set_max(new_max: int):
    global current_max
    current_max = new_max
    if "bar" in globals():
        if new_max == 0:
            bar.setRange(0, 0)
        else:
            bar.setRange(0, 100)
            bar.setValue(0)
    if "progress_label" in globals():
        progress_label.setText("安裝進度：0%")
    if "task_label" in globals():
        task_label.setText("目前沒有任務")


def analyze_and_show_log(log_text: str):
    result = check_minecraft_log(log_text)
    status = result["狀態"]
    message = result["關鍵詞"]
    try:
        with open("user_data/launcher_config.json", "r") as f:
            config = json.load(f)
            show_log = config.get("show_log_on_launch", False)
    except:
        show_log = False

    should_show_log = show_log or (status != "正常")
    if should_show_log:
        CommandWindow(log_text).exec_()

    if status == "正常":
        QMessageBox.information(None, "UMCL", f"Minecraft 已正常結束。\n關鍵：{message}")
    elif status == "異常":
        QMessageBox.critical(None, "UMCL", f"⚠ Minecraft 運行出錯\n{message}")
    elif status == "啟動失敗":
        QMessageBox.critical(None, "UMCL", f"❌ Minecraft 啟動失敗\n{message}")
    else:
        QMessageBox.warning(None, "UMCL", f"⚠ 無法判斷 Minecraft 是否正常結束\n（{message}）")

class CommandWindow(QDialog):
    def __init__(self, log_text: str):
        super().__init__()
        self.setWindowTitle("Minecraft 啟動日誌")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout(self)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(log_text)
        layout.addWidget(self.text_area)

        self.save_btn = QPushButton("保存日誌檔")
        self.save_btn.clicked.connect(lambda: self.save_log(log_text))
        layout.addWidget(self.save_btn)

        

    def save_log(self, log_text):
        outputfilename = "minecraft_log_output"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "保存日誌檔", os.path.join(home_path, f"{outputfilename}.log"),
            "Log日誌檔 (*.log);;All Files (*)"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(log_text)
                    f.write("\n")
                    f.write(f"[generated at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            except Exception as e:
                print("❌ 無法保存日誌檔案：", e)


class configwindow(QDialog):
    def __init__(self, event=None):
        super().__init__()
        self.setWindowTitle("設定")
        self.setGeometry(150, 150, 300, 200)
        layout = QVBoxLayout(self)

        self.show_log_var = QCheckBox("啟動時顯示日誌")
        layout.addWidget(self.show_log_var)

        try:
            with open("user_data/launcher_config.json", "r") as f:
                config = json.load(f)
                self.show_log_var.setChecked(config.get("show_log_on_launch", False))
        except:
            self.show_log_var.setChecked(False)

        self.show_log_var.stateChanged.connect(self.toggle_show_log)
        

    def toggle_show_log(self):
        config = {"show_log_on_launch": self.show_log_var.isChecked()}
        with open("user_data/launcher_config.json", "w") as f:
            json.dump(config, f, indent=2)


class UWPwindow(QDialog):
    def __init__(self, event=None):
        super().__init__()
        self.setWindowTitle("開啟UWP應用")
        self.setGeometry(200, 200, 400, 300)
        layout = QVBoxLayout(self)

        with open("user_data/MC_UWPid_lib.json", "r") as r:
            self.data = json.loads(r.read())
        self.options = self.data["edition"]

        self.combo = QComboBox()
        self.combo.addItems(self.options)
        layout.addWidget(self.combo)

        self.launch_btn = QPushButton("Launch!")
        self.launch_btn.clicked.connect(self.launch)
        layout.addWidget(self.launch_btn)

        

    def launch(self):
        selected = self.combo.currentText()
        if selected:
            try:
                subprocess.Popen(f"start shell:AppsFolder\\{self.data[selected]}", shell=True)
            except Exception as e:
                print(f"啟動失敗: {e}")


def save_bat(event=None):
    alya = core.Launcher()
    try:
        ver = selected_value if selected_value else (common_option["ver"] or options[0])
    except:
        ver = options[0]

    alya.normal(ver, width, height, False, "WafflyBat")
    outputfilename = f"{ver} export"
    filepath, _ = QFileDialog.getSaveFileName(
        None, "保存啟動腳本", os.path.join(home_path, f"{outputfilename}.bat"),
        "Windows 批次檔案 (*.bat);;All Files (*)"
    )
    if filepath:
        try:
            with open(filepath, "w") as f:
                f.write("@echo off\ncolor 2\n")
                f.write(f"echo 準備運行{ver}\n")
                with open("launch_cmd_temp.bat", "r") as rdf:
                    f.write(rdf.read())
                    f.write("\n")
                f.write("pause")
        except:
            print("路徑錯誤")


def play():
    alya = core.Launcher()
    yn = QMessageBox.question(None, "UMCL", "Do you want to play Minecraft?",
                               QMessageBox.Yes | QMessageBox.No)
    if yn == QMessageBox.Yes:
        try:
            ver = selected_value if selected_value else (common_option["ver"] or options[0])
        except:
            ver = options[0]
        alya.normal(ver, width, height, "WafflyBat")
        print("準備運行 : ", ver)
        install_in_thread(ver)


def on_select(index):
    global selected_value
    selected_value = combo.currentText()
    print(f"你選擇了: {selected_value}")
    with open("user_data/common.json", "w") as w:
        common_option["ver"] = selected_value
        json.dump(common_option, w, indent=2)


def disable_close(event=None):
    yn = QMessageBox.question(None, "UMCL", "是否關閉啟動器",
                               QMessageBox.Yes | QMessageBox.No)
    if yn == QMessageBox.Yes:
        sys.exit(0)


def system_check():
    if platform.system() == "Windows":
        win_ver = sys.getwindowsversion()
        if win_ver.build >= 10240:
            return True
    return False


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UMCL")
        self.setFixedSize(width, height)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - width) // 2, (screen.height() - height) // 2)

        icon_path = os.path.join(os.getcwd(), "art", "java.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.selected_value = None
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.vbox = QVBoxLayout(central_widget)

        self.launch_btn = QPushButton("launcher game")
        self.launch_btn.clicked.connect(play)
        self.vbox.addWidget(self.launch_btn)

        global combo, options
        options = core.Launcher.get_local_ver()
        combo = QComboBox()
        combo.addItems(options)
        combo.setCurrentIndex(0)
        combo.currentIndexChanged.connect(on_select)
        self.vbox.addWidget(combo)

        global bar, progress_label, task_label
        bar = QProgressBar()
        bar.setMaximum(100)
        bar.setValue(0)
        bar.setTextVisible(False)
        self.vbox.addWidget(bar)

        progress_label = QLabel("安裝進度：0%")
        self.vbox.addWidget(progress_label)

        task_label = QLabel("")
        task_label.setVisible(False)
        self.vbox.addWidget(task_label)

        self.init_menu()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show()

    def init_menu(self):
        global check_var
        check_var = QCheckBox()
        check_var.setChecked(common_option["toggle"])

        menubar = self.menuBar()

        file_menu = menubar.addMenu("檔案")
        save_script = QAction("保存啟動腳本", self)
        save_script.setShortcut("Alt+O")
        save_script.triggered.connect(save_bat)
        file_menu.addAction(save_script)

        game_menu = menubar.addMenu("基岩版啟動")
        is_bedrock = system_check()
        uwp_action = QAction("啟動本地", self)
        uwp_action.setShortcut("Alt+U")
        if is_bedrock:
            uwp_action.triggered.connect(lambda: UWPwindow().exec_())

        else:
            uwp_action.setEnabled(False)
        game_menu.addAction(uwp_action)

        config_menu = menubar.addMenu("設定")
        config_open = QAction("開啟設定", self)
        config_open.setShortcut("Alt+I")
        config_open.triggered.connect(lambda: configwindow().exec_())
        config_menu.addAction(config_open)

        quit_action = QAction("離開", self)
        quit_action.triggered.connect(disable_close)
        menubar.addAction(quit_action)

        self.addAction(self._make_shortcut("Alt+O", save_bat))
        self.addAction(self._make_shortcut("Alt+I", lambda: configwindow().exec_()))
        self.addAction(self._make_shortcut("Alt+U", lambda: UWPwindow().exec_()))
        self.addAction(self._make_shortcut("Alt+F4", disable_close))

    def _make_shortcut(self, key, func):
        action = QAction(self)
        action.setShortcut(key)
        action.triggered.connect(func)
        return action


def main_app():
    app = QApplication(sys.argv)
    window = MainApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    if not os.path.exists("user_data"):
        os.makedirs("user_data")
    if not os.path.exists("user_data/common.json"):
        with open("user_data/common.json", "w") as f:
            json.dump({"toggle": False, "ver": None}, f, indent=2)
    if not os.path.exists("user_data/MC_UWPid_lib.json"):
        with open("user_data/MC_UWPid_lib.json", "w") as f:
            json.dump({"edition": [], "UWPid": {}}, f, indent=2)

    main_app()

