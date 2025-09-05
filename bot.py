import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Telegram webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"status": "no_message"})

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text")

    if not text:
        return jsonify({"status": "no_text"})

    # Agar message ek Instagram link hai
    if "instagram.com" in text:
        try:
            # Download command with cookies
            cmd = [
                "yt-dlp",
                "--cookies", "cookies.txt",   # 👈 ye sabse important h
                "-o", "downloads/%(title)s.%(ext)s",
                text
            ]

            subprocess.run(cmd, check=True)

            return jsonify({"status": "downloaded", "url": text})

        except subprocess.CalledProcessError as e:
            return jsonify({"status": "error", "error": str(e)})

    return jsonify({"status": "ignored"})


@app.route("/")
def index():
    return "✅ Bot is running with cookies.txt"


if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    app.run(host="0.0.0.0", port=10000)
