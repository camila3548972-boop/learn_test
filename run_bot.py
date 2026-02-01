from flask import Flask, render_template, jsonify
from data_store import published_posts

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    """Serves the main frontend page."""
    return render_template("index.html")

@app.route('/api/posts')
def api_posts():
    """API endpoint to get posts from the shared data store."""
    formatted_posts = []
    for post_msg in published_posts:
        post_data = {
            "id": post_msg.message_id,
            "text": post_msg.text or post_msg.caption,
            "date": post_msg.date.isoformat(),
            "photo": post_msg.photo[-1].file_id if post_msg.photo else None,
            "video": post_msg.video.file_id if post_msg.video else None,
        }
        formatted_posts.append(post_data)
    return jsonify(formatted_posts)

# This part is no longer needed here as gunicorn will run the app
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)
