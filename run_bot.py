from bot_worker import create_app

# The Gunicorn server will run this app object
app = create_app()
