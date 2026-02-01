# This file acts as the WSGI entry point for Gunicorn.
# It imports the app factory from bot_worker and creates the app instance.

from bot_worker import create_app

# The Gunicorn server will look for this 'app' variable by default.
app = create_app()
