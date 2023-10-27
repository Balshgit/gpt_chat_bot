import base64
import json
import os
import threading
import time
import traceback

import execjs
from flask import Flask, request
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from werkzeug.serving import ThreadedWSGIServer

app = Flask(__name__)

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")


def deepai_refresh():
    while True:
        driver = webdriver.Chrome(options=options)
        try:
            driver.get("https://deepai.org")
            WebDriverWait(driver, 15)
            cookies = driver.get_cookies()
            print(cookies, flush=True)
        except Exception:
            traceback.print_exc()
        driver.quit()
        time.sleep(600)


# curl -X POST -d '{}' -H "Content-Type: application/json" http://127.0.0.1:8860/gptforlove
@app.route("/gptforlove", methods=["POST"])
def get_gptforlove_secret():
    dir = os.path.dirname(__file__)
    include = dir + "/npm/node_modules/crypto-js/crypto-js"
    source = """
CryptoJS = require({include})
var k = '14487141bvirvvG'
    , e = Math.floor(new Date().getTime() / 1e3);
var t = CryptoJS.enc.Utf8.parse(e)
    , o = CryptoJS.AES.encrypt(t, k, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
});
return o.toString()
"""
    source = source.replace("{include}", json.dumps(include))
    dict = {"secret": execjs.compile(source).call("")}
    return json.dumps(dict)


# curl -X POST -d '{}' -H "Content-Type: application/json" http://127.0.0.1:8860/vercel
@app.route("/vercel", methods=["POST"])
def get_anti_bot_token():
    request_body = json.loads(request.data)
    raw_data = json.loads(base64.b64decode(request_body["data"], validate=True))

    js_script = """const globalThis={marker:"mark"};String.prototype.fontcolor=function(){return `<font>${this}</font>`};
        return (%s)(%s)""" % (
        raw_data["c"],
        raw_data["a"],
    )

    raw_token = json.dumps(
        {"r": execjs.compile(js_script).call(""), "t": raw_data["t"]},
        separators=(",", ":"),
    )
    dict = {"data": base64.b64encode(raw_token.encode("utf-16le")).decode()}
    return json.dumps(dict)


if __name__ == "__main__":
    thread = threading.Thread(target=deepai_refresh)
    thread.start()
    port = os.getenv("PORT", "8860")
    ip = os.getenv("IP", "0.0.0.0")
    print(f"start zeus at {ip}:{port}", flush=True)
    server = ThreadedWSGIServer(ip, port, app)
    server.serve_forever()
