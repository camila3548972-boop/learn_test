from flask import render_template, jsonify
from bot_worker import create_app
from models import Post

# Use the application factory to create the app instance
app = create_app()

# Now define the routes for the created app
@app.route('/')
def index():
    """Serves the main frontend page."""
    return render_template("index.html")

@app.route('/api/posts')
def api_posts():
    """API endpoint to get posts from the database."""
    with app.app_context():
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
