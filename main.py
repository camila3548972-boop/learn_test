import time
from bot_worker import create_app
from database import db
from sqlalchemy.exc import OperationalError

# IMPORTANT: Import all your models here so that SQLAlchemy knows about them
from models import Post

app = create_app()

MAX_RETRIES = 10
RETRY_DELAY = 5  # seconds

for i in range(MAX_RETRIES):
    try:
        with app.app_context():
            print(f"Attempting to connect to the database (Attempt {i + 1}/{MAX_RETRIES})...")
            # This command will try to connect to the DB to create tables
            db.create_all()
            print("Database connection successful and tables created.")
            break  # Exit loop if successful
    except OperationalError as e:
        if i < MAX_RETRIES - 1:
            print(f"Database connection failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            print("Could not connect to the database after multiple retries. Giving up.")
            raise e
