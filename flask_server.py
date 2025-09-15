
from flask import Flask, request
from flask_cors import CORS

import subprocess



app = Flask(__name__)
CORS(app)


with open("vue.css", "r") as r:
    style=r.read()

@app.route('/from_scratch', methods=['GET', 'POST', 'HEAD'])
def from_scratch():
    data = request.headers
    data = str(data).splitlines()
    for i in data:
        if i.startswith("Command: "):
            cmd=i.lstrip("Command: ")
    
    print("來自 Scratch 的資料：\n", cmd)
    
    subprocess.Popen(f"explorer")

    return f"<!doctype html>\n<html lang=zh-tw>\n<title>successful get data</title>\n<style>{style}</style>\n<h1>OK,拿到資料了</h1>\n<p>{data}</p>"

# 啟動 Flask
def start():
    
    app.run(port=5000)

if __name__ == '__main__':
    start()

