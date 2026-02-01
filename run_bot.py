import logging
import asyncio
import threading
from flask import Flask, render_template, jsonify
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler
from dotenv import load_dotenv
import os

# Handlers
from handlers.start_handler import start_handler
from handlers.new_post_handler import new_post_conversation_handler
from handlers.edit_post_handler import edit_post_conversation_handler
from handlers.dm_handler import dm_conversation_handler
from handlers.restrict_user_handler import restrict_user_conversation_handler
from handlers.invite_handler import invite_handler
from handlers.livestream_handler import livestream_conversation_handler
from handlers.admin_panel_handler import admin_panel_handler, instruct_invite

# Import the shared data store
from data_store import published_posts

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Flask App ---
app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    """Serves the main frontend page."""
    return render_template("index.html")

@app.route('/api/posts')
def api_posts():
    """API endpoint to get posts from the shared data store."""
    formatted_posts = []
    for post_msg in published_posts:
        post_data = {
            "id": post_msg.message_id,
            "text": post_msg.text or post_msg.caption,
            "date": post_msg.date.isoformat(),
            "photo": post_msg.photo[-1].file_id if post_msg.photo else None,
            "video": post_msg.video.file_id if post_msg.video else None,
        }
        formatted_posts.append(post_data)
    return jsonify(formatted_posts)

def run_flask():
    """Runs the Flask app in a separate thread."""
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# --- Telegram Bot ---
def main() -> None:
    """Initializes and runs the Telegram bot."""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logging.critical("TELEGRAM_TOKEN environment variable not set.")
        return

    application = Application.builder().token(token).build()

    # Add command and conversation handlers
    application.add_handler(start_handler())
    application.add_handler(new_post_conversation_handler())
    application.add_handler(edit_post_conversation_handler())
    application.add_handler(dm_conversation_handler())
    application.add_handler(restrict_user_conversation_handler())
    application.add_handler(livestream_conversation_handler())
    application.add_handler(invite_handler())
    application.add_handler(admin_panel_handler())
    application.add_handler(CallbackQueryHandler(instruct_invite, pattern="^admin_instruct_invite$"))

    logging.info("Starting bot polling...")
    # run_polling() is a blocking call that runs the bot until CTRL+C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Start Flask app in a background daemon thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logging.info("Flask server started in a background thread.")

    # Run the bot's main function in the main thread
    main()
