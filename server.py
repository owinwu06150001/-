import os
from flask import Flask
from threading import Thread

app = Flask("keep_alive")

@app.route("/")
def home():
    return "Bot is alive!"

def run():
    # 優先使用 Render 提供的 PORT 環境變數
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run) # 使用執行緒避免阻斷主程式
    t.start()
