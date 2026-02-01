from telegram import Message
from models import db, Post

def publish_post(message: Message):
    """Publishes a post to the database."""
    new_post = Post(
        message_id=message.message_id,
        text=message.text or message.caption,
        photo_id=message.photo[-1].file_id if message.photo else None,
        video_id=message.video.file_id if message.video else None,
    )
    db.session.add(new_post)
    db.session.commit()


def get_all_posts():
    """Gets all posts from the database."""
    return Post.query.all()


def get_post_by_id(post_id: int):
    """Gets a post by its ID."""
    return Post.query.get(post_id)


def delete_post(post_id: int):
    """Deletes a post from the database."""
    post = get_post_by_id(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
