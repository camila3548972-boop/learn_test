from flask import Flask, render_template, jsonify
from database import db
from models import Post
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Ensure DATABASE_URL is set
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError("DATABASE_URL is not set. Please add it to your environment variables.")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    """Serves the main frontend page."""
    return render_template("index.html")

@app.route('/api/posts')
def api_posts():
    """API endpoint to get posts from the database."""
    posts = Post.query.order_by(Post.created_at.desc()).all()
    formatted_posts = []
    for post in posts:
        formatted_posts.append({
            'id': post.id,
            'message_id': post.message_id,
            'text': post.text,
            'photo_id': post.photo_id,
            'video_id': post.video_id,
            'created_at': post.created_at.isoformat()
        })
    return jsonify(formatted_posts)
