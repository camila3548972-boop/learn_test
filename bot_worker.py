import logging
import os
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler
from dotenv import load_dotenv

from database import db
from models import Post
from flask import Flask

# Import handlers
from handlers.start_handler import start_handler
from handlers.new_post_handler import new_post_conversation_handler
from handlers.edit_post_handler import edit_post_conversation_handler
from handlers.dm_handler import dm_conversation_handler
from handlers.restrict_user_handler import restrict_user_conversation_handler
from handlers.livestream_handler import livestream_conversation_handler
from handlers.invite_handler import invite_handler
from handlers.admin_panel_handler import admin_panel_handler, instruct_invite

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Ensure DATABASE_URL is set
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Please add it to your environment variables.")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def main() -> None:
    """Initializes and runs the Telegram bot."""
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.critical("TELEGRAM_TOKEN environment variable not set.")
        return

    app = create_app()
    with app.app_context():
        db.create_all()

        # Create the Application and pass it your bot's token.
        application = Application.builder().token(token).build()

        # Add all the handlers
        application.add_handler(start_handler())
        application.add_handler(new_post_conversation_handler())
        application.add_handler(edit_post_conversation_handler())
        application.add_handler(dm_conversation_handler())
        application.add_handler(restrict_user_conversation_handler())
        application.add_handler(livestream_conversation_handler())
        application.add_handler(invite_handler())
        application.add_handler(admin_panel_handler())
        application.add_handler(CallbackQueryHandler(instruct_invite, pattern="^admin_instruct_invite$"))

        # Start the Bot
        logger.info("Starting bot polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
