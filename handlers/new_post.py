import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Import shared resources
from config import (
    CHANNEL_ID, CATEGORIES, SELECTING_CATEGORY, TYPING_TYPE, TYPING_DETAILS, 
    AWAITING_MEDIA, ASKING_BUTTONS, TYPING_BUTTONS
)
from utils.publish import publish_post

# --- Conversation Entry Point ---

async def new_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status not in ['administrator', 'creator']:
            await update.message.reply_text("❌ Sorry, only admins can use this command.")
            return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        await update.message.reply_text(f"❌ Could not verify admin status. Error: {e}")
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data['media_album'] = []

    keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in CATEGORIES]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ Admin authorized. Choose a category:", reply_markup=reply_markup)
    return SELECTING_CATEGORY

# --- Conversation Steps ---

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["category"] = query.data
    await query.edit_message_text(text=f"Category set to '{query.data}'.\n\nNext, please send the 'Type'.")
    return TYPING_TYPE

async def type_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["type"] = update.message.text
    await update.message.reply_text("Type set. Now, send the main content (Details).")
    return TYPING_DETAILS

async def details_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["details"] = update.message.text
    keyboard = [[InlineKeyboardButton("Skip (Text-Only Post)", callback_data="skip_media")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Details received. Now, send one or more media files (photos/videos).\n"
        "When you have sent all files, type /done.\n"
        "Or press 'Skip' for a text-only post.",
        reply_markup=reply_markup
    )
    return AWAITING_MEDIA

async def media_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['media_album'].append(update.message)
    await update.message.reply_text(f"✅ Media #{len(context.user_data['media_album'])} received. Send more, or type /done.")
    return AWAITING_MEDIA

async def done_sending_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    media_count = len(context.user_data.get('media_album', []))
    if media_count > 1:
        await update.message.reply_text(f"Great, {media_count} files received. Publishing album... (No buttons for albums)")
        await publish_post(update, context)
        return ConversationHandler.END
    elif media_count == 1:
        keyboard = [
            [InlineKeyboardButton("Add Buttons ➕", callback_data="add_buttons")],
            [InlineKeyboardButton("Publish Now 🚀", callback_data="publish_now")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("One file received. Add buttons or publish?", reply_markup=reply_markup)
        return ASKING_BUTTONS
    else:
        return await skip_media(update, context, from_done=True)

async def skip_media(update: Update, context: ContextTypes.DEFAULT_TYPE, from_done: bool = False) -> int:
    keyboard = [
        [InlineKeyboardButton("Add Buttons ➕", callback_data="add_buttons")],
        [InlineKeyboardButton("Publish Now 🚀", callback_data="publish_now")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = "Skipping media. Do you want to add buttons?" if not from_done else "Do you want to add custom URL buttons?"

    if from_done:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)
    return ASKING_BUTTONS

async def go_to_typing_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Send button text and URL, separated by a comma.\n`Example: 👍 Like, https://url.com`\nSend /done when finished.")
    return TYPING_BUTTONS

async def publish_from_ask(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Publishing post...")
    await publish_post(update, context)
    return ConversationHandler.END

async def button_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    button_data = update.message.text.split(',', 1)
    if len(button_data) != 2:
        await update.message.reply_text("Invalid format. Use: `Text, http://url.com`\nSend /done to finish.")
        return TYPING_BUTTONS
    text, url = [x.strip() for x in button_data]
    if not url.startswith(('http://', 'https://')):
         await update.message.reply_text("Invalid URL. Try again or /done.")
         return TYPING_BUTTONS
    context.user_data.setdefault('buttons', []).append({'text': text, 'url': url})
    await update.message.reply_text(f"✅ Button '{text}' added. Add another, or /done.")
    return TYPING_BUTTONS

async def done_adding_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Buttons saved. Publishing post...")
    await publish_post(update, context)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = "Operation cancelled."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=msg)
    else:
        await update.message.reply_text(text=msg)
    context.user_data.clear()
    return ConversationHandler.END

# --- Build Handler --- 

new_post_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("newpost", new_post)],
    states={
        SELECTING_CATEGORY: [CallbackQueryHandler(category_selected)],
        TYPING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, type_received)],
        TYPING_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, details_received)],
        AWAITING_MEDIA: [
            MessageHandler(filters.PHOTO | filters.VIDEO, media_received),
            CommandHandler("done", done_sending_media),
            CallbackQueryHandler(skip_media, pattern="^skip_media$"),
        ],
        ASKING_BUTTONS: [
            CallbackQueryHandler(go_to_typing_buttons, pattern="^add_buttons$"),
            CallbackQueryHandler(publish_from_ask, pattern="^publish_now$"),
        ],
        TYPING_BUTTONS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, button_received),
            CommandHandler("done", done_adding_buttons),
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
