import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ConversationHandler, ContextTypes, CommandHandler, 
    MessageHandler, CallbackQueryHandler, filters
)

# Import shared config and utilities
from config import (
    CHANNEL_ID,
    SELECTING_POST_TO_EDIT, EDITING_POST, AWAITING_NEW_CAPTION # States
)
from .cancel_handler import cancel


# --- Conversation Entry Point (from Button) ---

async def edit_post_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the post editing conversation from a button press."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    # 1. Admin Check
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status not in ['administrator', 'creator']:
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
            await query.edit_message_text(
                text="❌ Sorry, only channel admins can edit posts.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END
    except Exception as e:
        await query.edit_message_text(f"❌ Could not verify admin status. Error: {e}")
        return ConversationHandler.END

    # 2. Start Conversation
    context.user_data.clear()
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="cancel")]]
    await query.edit_message_text(
        text="Okay, let's edit a post. Please forward the message from the channel to me.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECTING_POST_TO_EDIT

# --- Other states (post_to_edit_received, select_edit_caption, etc.) remain largely the same ---

async def post_to_edit_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the forwarded message and asks what to edit."""
    if not update.message.forward_from_chat or update.message.forward_from_chat.id != int(CHANNEL_ID):
        keyboard = [
            [InlineKeyboardButton("EA Try Again", callback_data="edit_post_start")],
            [InlineKeyboardButton("🔙 Cancel", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"❌ That was not a valid forwarded message. Please forward a post from the channel.",
            reply_markup=reply_markup
        )
        return SELECTING_POST_TO_EDIT

    context.user_data['edit_post_id'] = update.message.forward_from_message_id
    logging.info(f"Editing message ID: {context.user_data['edit_post_id']}")

    keyboard = [
        [InlineKeyboardButton("📝 Edit Caption / Text", callback_data="edit_caption")],
        # [InlineKeyboardButton("🎛️ Edit Buttons", callback_data="edit_buttons")], # Placeholder for future
        [InlineKeyboardButton("🔙 Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ Post selected. What would you like to edit?", reply_markup=reply_markup)

    return EDITING_POST

async def select_edit_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks the user to send the new caption/text for the post."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(text="Please send the new caption for the post. You can /cancel at any time.")
    
    return AWAITING_NEW_CAPTION

async def caption_received_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the new caption and edits the message in the channel."""
    new_caption = update.message.text
    post_to_edit_id = context.user_data.get('edit_post_id')

    if not post_to_edit_id:
        await update.message.reply_text("Error: Couldn't find the post to edit. Please start over.")
        context.user_data.clear()
        return ConversationHandler.END
    
    response_message = None
    try:
        # Attempt to edit the message caption in the channel
        await context.bot.edit_message_caption(
            chat_id=CHANNEL_ID,
            message_id=post_to_edit_id,
            caption=new_caption
        )
        response_message = "✅ Caption updated successfully in the channel!"
        
    except Exception as e:
        logging.warning(f"Could not edit caption, trying to edit text. Error: {e}")
        # Handle cases where the message is text-only (has no caption)
        try:
            await context.bot.edit_message_text(
                text=new_caption,
                chat_id=CHANNEL_ID,
                message_id=post_to_edit_id
            )
            response_message = "✅ Text updated successfully in the channel!"
        except Exception as inner_e:
            logging.error(f"Failed to edit text for message {post_to_edit_id}: {inner_e}")
            response_message = f"❌ Failed to update the post. Error: {inner_e}"

    # Go back to the main menu
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
    await update.message.reply_text(response_message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    context.user_data.clear()
    return ConversationHandler.END


# --- Conversation Handler Setup ---

def edit_post_conversation_handler() -> ConversationHandler:
    """Creates the ConversationHandler for the post editing workflow, starting from a button press."""
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_post_start, pattern="^edit_post_start$")],
        states={
            SELECTING_POST_TO_EDIT: [
                MessageHandler(filters.FORWARDED, post_to_edit_received)
            ],
            EDITING_POST: [
                CallbackQueryHandler(select_edit_caption, pattern="^edit_caption$")
            ],
            AWAITING_NEW_CAPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, caption_received_for_edit)
            ]
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^cancel$") # Generic cancel button
        ],
        per_message=False,
         map_to_parent={
            ConversationHandler.END: ConversationHandler.END,
        }
    )
