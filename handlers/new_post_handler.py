import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Import shared config and utilities
from config import (
    CHANNEL_ID, CATEGORIES,
    SELECTING_CATEGORY, TYPING_TYPE, TYPING_DETAILS, AWAITING_MEDIA, ASKING_BUTTONS, TYPING_BUTTONS
)
from utils.publish import publish_post # Correctly import from utils
from .cancel_handler import cancel

# --- Conversation Entry Point (from Button) ---

async def new_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the new post conversation from a button press, after checking admin rights."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    # 1. Admin Check
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status not in ['administrator', 'creator']:
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
            await query.edit_message_text(
                text="❌ Sorry, only channel admins can create posts.", 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        await query.edit_message_text(f"❌ Could not verify admin status. Error: {e}")
        return ConversationHandler.END

    # 2. Clear previous data and start conversation
    context.user_data.clear()
    context.user_data['media_album'] = []

    keyboard = [[InlineKeyboardButton(cat, callback_data=cat)] for cat in CATEGORIES]
    keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="✅ Admin authorized. Let's create a new post.\n\nFirst, choose a category:", 
        reply_markup=reply_markup
    )
    return SELECTING_CATEGORY

# --- Other states remain the same ---
async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["category"] = query.data
    await query.edit_message_text(text=f"Category set to '{query.data}'.\n\nNext, please send the 'Type'.")
    return TYPING_TYPE

async def type_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["type"] = update.message.text
    await update.message.reply_text("Type set. Now, please send the main content (Details).")
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
        await update.message.reply_text(f"Received {media_count} files. Publishing album... (Buttons not supported for albums)")
        await publish_post(update, context)
        return ConversationHandler.END
    elif media_count == 1:
        keyboard = [
            [InlineKeyboardButton("Add Buttons ➕", callback_data="add_buttons")],
            [InlineKeyboardButton("Publish Now 🚀", callback_data="publish_now")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("One file received. Would you like to add buttons or publish now?", reply_markup=reply_markup)
        return ASKING_BUTTONS
    else: # media_count == 0
        await update.message.reply_text("No media sent. Proceeding with a text-only post.")
        return await skip_media(update, context, from_done=True)

async def skip_media(update: Update, context: ContextTypes.DEFAULT_TYPE, from_done: bool = False) -> int:
    keyboard = [
        [InlineKeyboardButton("Add Buttons ➕", callback_data="add_buttons")],
        [InlineKeyboardButton("Publish Now 🚀", callback_data="publish_now")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message_text = "Do you want to add custom URL buttons?"
    if from_done:
        await update.message.reply_text(message_text, reply_markup=reply_markup)
    else:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(f"Skipping media. {message_text}", reply_markup=reply_markup)
    return ASKING_BUTTONS

async def go_to_typing_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data.setdefault('buttons', [])
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
        await update.message.reply_text("Invalid URL (must start with http/https). Try again or /done.")
        return TYPING_BUTTONS
    context.user_data.setdefault('buttons', []).append({'text': text, 'url': url})
    await update.message.reply_text(f"✅ Button '{text}' added. Add another, or /done.")
    return TYPING_BUTTONS

async def done_adding_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Buttons saved. Publishing post...")
    await publish_post(update, context)
    return ConversationHandler.END

# --- Conversation Handler Setup ---

def new_post_conversation_handler() -> ConversationHandler:
    """Creates the ConversationHandler for the new post workflow."""
    category_pattern = f"^({'|'.join(CATEGORIES)})$"
    
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(new_post_start, pattern="^new_post_start$")],
        states={
            SELECTING_CATEGORY: [CallbackQueryHandler(category_selected, pattern=category_pattern)],
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
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^cancel$")
        ],
        per_message=False,
        map_to_parent={ ConversationHandler.END: ConversationHandler.END }
    )
