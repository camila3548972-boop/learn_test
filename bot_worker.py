from flask import Flask
from telegram.ext import Application
import os

def create_app():
    app = Flask(__name__)
    # Your Flask app configurations can go here
    return app

# This part is for the Telegram bot worker, not the web server.
# It should not be run when the web server starts.
if __name__ != '__main__':
    # Assume TOKEN is set in the environment for the worker
    TOKEN = os.environ.get("TOKEN")
    if TOKEN:
        application = Application.builder().token(TOKEN).build()

        # Import handlers here, inside the condition
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

        # Note: The following line is blocking and should be in its own script for the worker
        # application.run_polling()
    else:
        # This will be printed when the web server starts, which is expected
        print("TOKEN environment variable not found, bot worker not started.")
