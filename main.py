from bot_worker import create_app
from database import db

# IMPORTANT: Import all your models here so that SQLAlchemy knows about them
from models import Admin, AppConfig, Channel, User, UserChannel

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully.")
