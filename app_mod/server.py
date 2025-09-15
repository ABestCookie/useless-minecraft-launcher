from http.server import HTTPServer, SimpleHTTPRequestHandler
from functools import partial
import os
import logging
logging.basicConfig(
    level=logging.DEBUG,  # 設定最低輸出等級
    filename="debug.log",
    filemode="a",  # 覆蓋用 "w"，追加用 "a"
    format="%(asctime)s [%(levelname)s] %(message)s"
)

httpd = None  # 全域變數

def run_server(ROOT):
    global httpd
    logging.info(f"Server script is running on {os.getcwd()}")
    PORT = 1936
    


    handler_class = partial(SimpleHTTPRequestHandler, directory=ROOT)

    httpd = HTTPServer(("", PORT), handler_class)

    logging.info(f"Serving {ROOT} at http://localhost:{PORT}/")
    httpd.serve_forever()

def stop_server():
    global httpd
    if httpd:
        logging.info("Stopping server...")
        httpd.shutdown()
        httpd.server_close()
        httpd = None
    else:
        logging.warning("Server not running.")



