import eel
import os
import sys
import logging
import time
import threading
import json
import app_mod.account as account
import app_mod.skin as skin
import app_mod.server as server
import tkinter.messagebox as messagebox
eel.init(".")
eel.start('ui.html', size=(800, 600))
logging.basicConfig(
    level=logging.DEBUG,
    filename="debug.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s"
)
