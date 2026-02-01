import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters,
    CommandHandler
)

from config import AWAITING_DM_USER_ID, AWAITING_DM_MESSAGE
from .cancel_handler import cancel # Import generic cancel handler

# --- Start DM Flow ---

async def dm_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for the user ID to send a direct message to."""
    query = update.callback_query
    await query.answer()

    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="💬 Please send me the Telegram User ID of the person you want to message.\n\n"
             "You can get the user's ID by forwarding a message from them to a bot like @userinfobot.",
        reply_markup=reply_markup
    )
    return AWAITING_DM_USER_ID

# --- Handle User ID Input ---

async def dm_receive_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the user ID and asks for the message to send."""
    user_id_str = update.message.text
    try:
        user_id = int(user_id_str)
        context.user_data['dm_user_id'] = user_id
        await update.message.reply_text(
            f"✅ User ID set to `{user_id}`.\n\nNow, please send me the full message you want to deliver. Or /cancel to stop.",
            parse_mode='Markdown'
        )
        return AWAITING_DM_MESSAGE
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid User ID. Please send a valid Telegram User ID (which is a number). Or /cancel to stop."
        )
        return AWAITING_DM_USER_ID

# --- Handle Message and Send ---

async def dm_receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends the collected message to the target user and ends the conversation."""
    user_id_to_dm = context.user_data.get('dm_user_id')
    message_to_send = update.message.text
    admin_user = update.effective_user

    if not user_id_to_dm:
        await update.message.reply_text("Error: User ID was not found. Please start over.")
        context.user_data.clear()
        return ConversationHandler.END

    try:
        await context.bot.send_message(
            chat_id=user_id_to_dm,
            text=message_to_send
        )
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        await update.message.reply_text(
            f"✅ Message successfully sent to user `{user_id_to_dm}`.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        logging.info(f"Admin {admin_user.name} sent a DM to user {user_id_to_dm}")

    except Exception as e:
        logging.error(f"Failed to send DM to {user_id_to_dm} by admin {admin_user.name}: {e}")
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        await update.message.reply_text(
            f"❌ Failed to send message to user `{user_id_to_dm}`.\n\nError: {e}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    context.user_data.clear()
    return ConversationHandler.END


# --- Conversation Handler Setup ---

def dm_conversation_handler() -> ConversationHandler:
    """Creates the conversation handler for sending a direct message."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(dm_start, pattern="^admin_dm_user$")],
        states={
            AWAITING_DM_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, dm_receive_user_id)],
            AWAITING_DM_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, dm_receive_message)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^cancel$")
        ],
        map_to_parent={ ConversationHandler.END: ConversationHandler.END },
        per_message=False,
    )
