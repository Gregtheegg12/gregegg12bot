import telebot
import requests
import os
from flask import Flask, send_from_directory

# Replace with your actual bot token
TOKEN = 8114644328:AAFn7fbVj6J6HTcjShG5ySpnOZ-u_S6wiSY
bot = telebot.TeleBot(TOKEN)

# Create a folder to store files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask app to serve files
app = Flask(__name__)

# Handle files sent to the bot
@bot.message_handler(content_types=['document', 'photo', 'video'])
def handle_files(message):
    file_id = None
    file_name = None

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.photo:
        file_id = message.photo[-1].file_id  # Get highest resolution photo
        file_name = f"photo_{message.chat.id}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{message.chat.id}.mp4"

    # Get file path from Telegram
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

    # Save file locally
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    response = requests.get(file_url, stream=True)
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    # Generate download link
    public_url = f"https://yourserver.com/download/{file_name}"
    bot.reply_to(message, f"Download your file here: {public_url}")

# Flask route to serve files
@app.route("/download/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Start the bot
def start_bot():
    bot.polling()

if __name__ == "__main__":
    from threading import Thread
    Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
