from flask import Flask
from telegram.ext import Application
import os
from database import db

def create_app():
    app = Flask(__name__)
    
    # Check for DATABASE (Railpack convention) or DATABASE_URL (standard convention)
    database_url = os.environ.get('DATABASE') or os.environ.get('DATABASE_URL')
    
    # Add a print statement for clear debugging in Railway logs
    print(f"DEBUG: Attempting to use database URL: {database_url}")
    
    if database_url:
        # SQLAlchemy prefers 'postgresql://' over 'postgres://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # This will help confirm if the environment variable is missing
        print("ERROR: DATABASE or DATABASE_URL environment variable not found.")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/')
    def index():
        return "Web server is running!"

    return app

def run_bot():
    TOKEN = os.environ.get("TOKEN")
    if TOKEN:
        application = Application.builder().token(TOKEN).build()
        print("Bot worker is running...")
        # Add your bot handlers here
        application.run_polling()
    else:
        print("ERROR: TOKEN environment variable not found. Bot cannot start.")
