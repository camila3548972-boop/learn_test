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

from config import CHANNEL_ID, AWAITING_RESTRICT_USER_ID
from .cancel_handler import cancel

# --- Start Restriction Flow ---

async def restrict_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the admin for the user ID to restrict."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="🚫 *Restrict User*\n\nPlease send me the Telegram User ID of the person you want to permanently ban from the channel.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return AWAITING_RESTRICT_USER_ID

# --- Process User ID and Ban ---

async def restrict_user_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the user ID and attempts to ban the user."""
    admin_user = update.effective_user
    user_id_to_restrict_str = update.message.text

    # --- Input Validation ---
    if not user_id_to_restrict_str.isdigit():
        keyboard = [[InlineKeyboardButton("🔙 Try Again", callback_data="admin_restrict_user")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ Invalid format. Please send a valid Telegram User ID (which is a number).",
            reply_markup=reply_markup
        )
        return AWAITING_RESTRICT_USER_ID # Stay in the same state

    user_id_to_restrict = int(user_id_to_restrict_str)

    # --- Self-Ban Check ---
    if user_id_to_restrict == admin_user.id:
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_panel_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "❌ You cannot restrict yourself.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    # --- Execution & Error Handling ---
    try:
        await context.bot.ban_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id_to_restrict
        )
        
        logging.info(f"Admin {admin_user.name} banned user {user_id_to_restrict} from channel {CHANNEL_ID}.")

        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_panel_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"✅ Success! User `{user_id_to_restrict}` has been permanently banned from the channel.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        logging.error(f"Failed to ban user {user_id_to_restrict}: {e}")
        error_message = str(e).lower()
        
        reply_text = f"❌ An unexpected error occurred: {e}"
        if "user not found" in error_message:
            reply_text = f"❌ Failed to ban user. Reason: User `{user_id_to_restrict}` not found."
        elif "bot is not a member" in error_message or "chat not found" in error_message:
            reply_text = "❌ *Action Failed!*\n\nI am not an admin in the channel, or I lack the 'Ban Users' permission."
        elif "can't remove chat owner" in error_message:
            reply_text = "❌ *Action Failed!*\n\nYou cannot restrict the owner of the channel."

        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_panel_start")]]
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            
    return ConversationHandler.END


# --- Conversation Handler Setup ---

def restrict_user_conversation_handler() -> ConversationHandler:
    """Creates the ConversationHandler for the user restriction workflow."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(restrict_user_start, pattern="^admin_restrict_user$")],
        states={
            AWAITING_RESTRICT_USER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, restrict_user_id_received)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^cancel$")
        ],
        per_user=True,
        per_chat=True,
    )