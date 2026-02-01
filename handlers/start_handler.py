import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler

# Define a state for the main menu
MAIN_MENU = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the main menu and returns the state for the conversation."""
    web_app_url = os.getenv("WEB_APP_URL", "https://www.google.com")
    keyboard = [
        [InlineKeyboardButton("🚀 Open Mini App", web_app=WebAppInfo(url=web_app_url))],
        [InlineKeyboardButton("📝 New Post", callback_data="new_post_start")],
        [InlineKeyboardButton("✏️ Edit Post", callback_data="edit_post_start")],
        [InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel_start")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    menu_text = "👋 Welcome! I am your Channel Management Bot.\n\nChoose an option to get started:"

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=menu_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=menu_text, reply_markup=reply_markup)
    
    return MAIN_MENU

def start_handler() -> ConversationHandler:
    """Creates a ConversationHandler for the main menu."""
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                # When these buttons are pressed, end this conversation
                # so that other handlers can pick up the callback query.
                CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^new_post_start$"),
                CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^edit_post_start$"),
                CallbackQueryHandler(lambda u, c: ConversationHandler.END, pattern="^admin_panel_start$"),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        map_to_parent={
            ConversationHandler.END: ConversationHandler.END
        }
    )
