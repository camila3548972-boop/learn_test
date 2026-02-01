import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from config import CHANNEL_ID

async def publish_post(update, context):
    """Publishes the post to the channel based on user_data."""
    user_data = context.user_data
    if update.callback_query:
        admin_chat_id = update.callback_query.message.chat_id
    else:
        admin_chat_id = update.message.chat_id

    try:
        caption = (
            f"Category: #{user_data['category']}\n"
            f"Type: {user_data['type']}\n\n"
            f"{user_data['details']}"
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
            await context.bot.send_media_group(chat_id=CHANNEL_ID, media=media_group)
        elif len(media_album) == 1:
            msg = media_album[0]
            if msg.photo:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=msg.photo[-1].file_id, caption=caption, reply_markup=reply_markup)
            elif msg.video:
                await context.bot.send_video(chat_id=CHANNEL_ID, video=msg.video.file_id, caption=caption, reply_markup=reply_markup)
            elif msg.document:
                await context.bot.send_document(chat_id=CHANNEL_ID, document=msg.document.file_id, caption=caption, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, reply_markup=reply_markup)

        await context.bot.send_message(chat_id=admin_chat_id, text="✅ Post successfully published!")

    except Exception as e:
        logging.error(f"Error publishing post: {e}")
        await context.bot.send_message(chat_id=admin_chat_id, text=f"❌ Failed to publish post. Error: {e}")
    finally:
        user_data.clear()
