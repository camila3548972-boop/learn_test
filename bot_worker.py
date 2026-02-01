from flask import Flask
from telegram.ext import Application
import os
from database import db
from dotenv import load_dotenv

load_dotenv()

def create_app():
    """Application Factory: Creates and configures the Flask app."""
    app = Flask(__name__)
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set. Please add it to your environment variables.")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy with the app instance
    db.init_app(app)

    return app

# This part is for the Telegram bot worker, not the web server.
if __name__ != '__main__':
    TOKEN = os.environ.get("TOKEN")
    if TOKEN:
        application = Application.builder().token(TOKEN).build()

        from handlers.start import start_handler
        from handlers.new_post import new_post_handler
        from handlers.admin_panel_handler import admin_panel_handler
        from handlers.dm_handler import dm_handler
        from handlers.edit_post_handler import edit_post_handler
        from handlers.cancel_handler import cancel_handler

        application.add_handler(start_handler)
        application.add_handler(new_post_handler)
        application.add_handler(admin_panel_handler)
        application.add_handler(dm_handler)
        application.add_handler(edit_post_handler)
        application.add_handler(cancel_handler)
    else:
        print("TOKEN environment variable not found, bot worker not started.")
