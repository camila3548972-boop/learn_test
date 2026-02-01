from database import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.BigInteger, unique=True, nullable=False)
    text = db.Column(db.Text, nullable=True)
    photo_id = db.Column(db.String(255), nullable=True)
    video_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Post {self.id}>'