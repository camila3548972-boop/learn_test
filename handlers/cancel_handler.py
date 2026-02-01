from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the current conversation."""
    msg = "Operation cancelled."
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=msg)
    else:
        await update.message.reply_text(text=msg)
    
    # Clear any user data stored for the conversation
    context.user_data.clear()
    
    # End the conversation
    return ConversationHandler.END
