from flask import Flask, request
import yt_dlp
import os
import requests

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # apna bot token yaha daalo
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

app = Flask(__name__)

def download_instagram(url):
    ydl_opts = {
        "cookies": "cookies.txt",  # cookies.txt file use karega
        "outtmpl": "%(title)s.%(ext)s",
        "format": "mp4",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def send_message(chat_id, text):
    requests.post(BASE_URL + "sendMessage", data={"chat_id": chat_id, "text": text})

def send_video(chat_id, file_path):
    with open(file_path, "rb") as f:
        requests.post(BASE_URL + "sendVideo", data={"chat_id": chat_id}, files={"video": f})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    if "instagram.com" in text:
        send_message(chat_id, "⏳ Downloading your Instagram video...")

        try:
            file_path = download_instagram(text)
            send_video(chat_id, file_path)
            os.remove(file_path)  # file delete after sending
        except Exception as e:
            send_message(chat_id, f"❌ Error: {str(e)}")
    else:
        send_message(chat_id, "👋 Send me an Instagram link to download.")

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)