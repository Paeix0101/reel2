import os
import re
import logging
import tempfile
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# --- Config ---
TOKEN = os.getenv("BOT_TOKEN")  # set BOT_TOKEN in Render environment
URL = os.getenv("APP_URL")      # e.g. https://your-service.onrender.com
PORT = int(os.environ.get("PORT", 10000))

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Flask app ---
flask_app = Flask(__name__)

# --- Telegram Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me any Instagram Reel link and I’ll DM you the video!")

async def handle_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "instagram.com/reel/" in text:
        user_id = update.message.from_user.id
        await update.message.reply_text("⏳ Downloading your reel...")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    "outtmpl": f"{tmpdir}/%(id)s.%(ext)s",
                    "format": "mp4[height<=720]+bestaudio/best[ext=mp4]/mp4",
                    "quiet": True,
                    "merge_output_format": "mp4"
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(text, download=True)
                    filename = ydl.prepare_filename(info)

                # Send reel privately to user
                await context.bot.send_video(chat_id=user_id, video=open(filename, "rb"))

            await update.message.reply_text("✅ Sent to your private chat!")

        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Failed to download this reel. Make sure the link is correct or the reel is public.")

# --- Main ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reel))

    # Flask route for Telegram webhook
    @flask_app.route(f"/{TOKEN}", methods=["POST"])
    def webhook():
        update = Update.de_json(request.get_json(force=True), app.bot)
        app.update_queue.put(update)
        return "ok", 200

    # Set webhook
    async def set_webhook():
        await app.bot.set_webhook(url=f"{URL}/{TOKEN}")

    app.create_task(set_webhook())  # schedule webhook setup

    # Start Flask server (Render runs this)
    flask_app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()