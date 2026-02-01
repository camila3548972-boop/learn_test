from flask import Flask
from telegram.ext import Application
import os
from database import db

def create_app():
    app = Flask(__name__)
    # Railpack requires the secret to be named DATABASE
    database_url = os.environ.get('DATABASE')
    
    if database_url:
        # Railway provides a 'postgres://' URL, but SQLAlchemy prefers 'postgresql://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Add a simple root route to check if the app is running
    @app.route('/')
    def index():
        return "Web server is running!"

    return app

# This part is for the Telegram bot worker
def run_bot():
    TOKEN = os.environ.get("TOKEN")
    if TOKEN:
        application = Application.builder().token(TOKEN).build()
        # You would add your handlers (commands, messages, etc.) here
        # For now, we'll just log that the bot is running
        print("Bot is running...")
