
from bot_worker import create_app
from database import db

# Use the application factory to get the app instance
app = create_app()

# Push an application context before working with the database
with app.app_context():
    # Now the db object knows about the app
    db.create_all()
    print("Database tables created successfully.")
