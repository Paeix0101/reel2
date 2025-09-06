import os
import requests
import yt_dlp
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_CHAT_ID")  # Replace with your ID

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        url = data["message"]["text"]
        video_path = download_instagram(url)
        if video_path:
            send_to_telegram(video_path)
            return jsonify({"status": "ok", "file": video_path})
    return jsonify({"status": "ignored"})

def download_instagram(url):
    try:
        ydl_opts = {
            "outtmpl": "downloads/%(title).50s.%(ext)s",
            "cookies": "cookies.txt"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print("Download error:", e)
        return None

def send_to_telegram(file_path):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        with open(file_path, "rb") as f:
            res = requests.post(url, data={"chat_id": CHAT_ID}, files={"video": f})
        print("Telegram response:", res.json())
    except Exception as e:
        print("Telegram send error:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
