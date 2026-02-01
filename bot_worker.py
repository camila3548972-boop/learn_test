from flask import Flask
from telegram.ext import Application
import os
from database import db

def create_app():
    app = Flask(__name__)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Railway uses 'postgres://', but SQLAlchemy prefers 'postgresql://'
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

        print("Bot worker started polling...")
        application.run_polling()
    else:
        print("TOKEN environment variable not found, bot worker not started.")

# This block will only run when the script is executed directly (for the worker)
if __name__ == '__main__':
    run_bot()
