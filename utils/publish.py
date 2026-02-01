import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes

# Import config variables
from config import CHANNEL_ID
# Import the shared data store
from data_store import published_posts

async def publish_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Formats, publishes the post, and stores it in the shared data store."""
    user_data = context.user_data
    if update.callback_query:
        admin_chat_id = update.callback_query.message.chat_id
    else:
        admin_chat_id = update.message.chat_id

    sent_messages = []
    try:
        caption = (
            f"Category: #{user_data.get('category', 'N/A')}\n"
            f"Type: {user_data.get('type', 'N/A')}\n\n"
            f"{user_data.get('details', '')}"
        )

        reply_markup = None
        if user_data.get('buttons'):
            keyboard = [[InlineKeyboardButton(text=btn['text'], url=btn['url'])] for btn in user_data['buttons']]
            if keyboard:
                reply_markup = InlineKeyboardMarkup(keyboard)

        media_album = user_data.get('media_album', [])

        if len(media_album) > 1:
            media_group = []
            for i, msg in enumerate(media_album):
                media_caption = caption if i == 0 else None
                if msg.photo:
                    media_group.append(InputMediaPhoto(media=msg.photo[-1].file_id, caption=media_caption))
                elif msg.video:
                    media_group.append(InputMediaVideo(media=msg.video.file_id, caption=media_caption))
            sent_messages = await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)

        elif len(media_album) == 1:
            msg = media_album[0]
            if msg.photo:
                sent_message = await context.bot.send_photo(chat_id=CHANNEL_ID, photo=msg.photo[-1].file_id, caption=caption, reply_markup=reply_markup)
            elif msg.video:
                sent_message = await context.bot.send_video(chat_id=CHANNEL_ID, video=msg.video.file_id, caption=caption, reply_markup=reply_markup)
            elif msg.document:
                sent_message = await context.bot.send_document(chat_id=CHANNEL_ID, document=msg.document.file_id, caption=caption, reply_markup=reply_markup)
            sent_messages = [sent_message] # Always a list

        else: # Text-only
            sent_message = await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=reply_markup)
            sent_messages = [sent_message]

        await context.bot.send_message(chat_id=admin_chat_id, text="✅ Post successfully published to the channel!")
        
        # --- Store in Data Store ---
        if sent_messages:
            # Prepend new posts to the beginning of the list
            published_posts[:0] = sent_messages

    except Exception as e:
        logging.error(f"Error publishing post: {e}")
        await context.bot.send_message(chat_id=admin_chat_id, text=f"❌ Failed to publish post. Error: {e}")
    finally:
        user_data.clear()
