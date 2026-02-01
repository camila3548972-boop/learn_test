import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
)

from config import (
    CHANNEL_ID,
    LIVESTREAM_MESSAGE_TAG,
    SELECTING_LIVESTREAM_ACTION,
    AWAITING_LIVESTREAM_TITLE,
    AWAITING_LIVESTREAM_LINK,
)
from .cancel_handler import cancel

# --- Main Entry Point ---


async def livestream_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Displays the livestream management menu."""
    query = update.callback_query
    await query.answer()

    active_livestream_msg_id = context.bot_data.get("active_livestream_message_id")

    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Start New Livestream", callback_data="livestream_begin_start_flow"
            )
        ],
    ]

    if active_livestream_msg_id:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "⏹️ Stop Active Livestream", callback_data="livestream_stop"
                )
            ]
        )

    keyboard.append(
        [InlineKeyboardButton("🔙 Back to Admin Menu", callback_data="admin_panel_start")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=("🚀 *Livestream Management*\n\n"
              "Here you can announce a new livestream to the channel or stop an existing one."),
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )
    return SELECTING_LIVESTREAM_ACTION


# --- Start Flow ---


async def livestream_ask_for_title(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Asks for the livestream title."""
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Enter the title for the livestream announcement.",
        reply_markup=reply_markup,
    )
    return AWAITING_LIVESTREAM_TITLE


async def livestream_receive_title(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives the title and asks for the link."""
    context.user_data["livestream_title"] = update.message.text
    await update.message.reply_text(
        "Title saved. Now, please send the link for the livestream."
    )
    return AWAITING_LIVESTREAM_LINK


async def livestream_receive_link_and_announce(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Receives the link, posts the announcement, and ends the conversation."""
    admin_user = update.effective_user
    title = context.user_data.get("livestream_title")
    link = update.message.text

    if not all([title, link, CHANNEL_ID]):
        await update.message.reply_text(
            "❌ An error occurred. Missing title, link, or channel ID. Please start over."
        )
        if "livestream_title" in context.user_data:
            del context.user_data["livestream_title"]
        return ConversationHandler.END

    announcement_text = (
        f"🔴 LIVE NOW! 🔴\n\n"
        f"*{title}*\n\n"
        f"Join us live at the link below!\n"
        f"👇👇👇\n"
        f"{link}\n\n"
        f"{LIVESTREAM_MESSAGE_TAG}"
    )

    try:
        sent_message = await context.bot.send_message(
            chat_id=CHANNEL_ID, text=announcement_text, parse_mode="Markdown"
        )
        context.bot_data["active_livestream_message_id"] = sent_message.message_id
        await update.message.reply_text(
            "✅ Livestream announced successfully in the channel!"
        )
        logging.info(f"Admin {admin_user.name} started livestream '{title}'")

    except Exception as e:
        logging.error(f"Failed to announce livestream: {e}")
        await update.message.reply_text(f"❌ Failed to post announcement. Error: {e}")

    if "livestream_title" in context.user_data:
        del context.user_data["livestream_title"]

    return ConversationHandler.END


# --- Stop Flow ---


async def livestream_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stops an active livestream by deleting the announcement and posting an 'ended' message."""
    query = update.callback_query
    await query.answer()
    admin_user = update.effective_user

    livestream_message_id = context.bot_data.get("active_livestream_message_id")

    if not livestream_message_id:
        await query.edit_message_text(
            "ℹ️ There is no active livestream announcement to stop."
        )
        return ConversationHandler.END

    try:
        await context.bot.delete_message(
            chat_id=CHANNEL_ID, message_id=livestream_message_id
        )
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text="✅ The livestream has now ended. Thanks for joining!",
        )
        await query.edit_message_text(
            "✅ Livestream stopped successfully and announcement removed."
        )
        logging.info(
            f"Admin {admin_user.name} stopped livestream (message_id: {livestream_message_id})"
        )
        del context.bot_data["active_livestream_message_id"]

    except Exception as e:
        logging.error(
            f"Error stopping livestream (message_id: {livestream_message_id}): {e}"
        )
        await query.edit_message_text(
            f"❌ Could not stop the livestream. It might have been deleted already. Error: {e}"
        )
        if "active_livestream_message_id" in context.bot_data:
            del context.bot_data["active_livestream_message_id"]

    return ConversationHandler.END


# --- Handler Setup ---


def livestream_conversation_handler() -> ConversationHandler:
    """Creates the conversation handler for managing livestreams."""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(livestream_start, pattern="^admin_livestream$")
        ],
        states={
            SELECTING_LIVESTREAM_ACTION: [
                CallbackQueryHandler(
                    livestream_ask_for_title, pattern="^livestream_begin_start_flow$"
                ),
                CallbackQueryHandler(livestream_stop, pattern="^livestream_stop$"),
            ],
            AWAITING_LIVESTREAM_TITLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, livestream_receive_title
                )
            ],
            AWAITING_LIVESTREAM_LINK: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    livestream_receive_link_and_announce,
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel, pattern="^cancel$"),
        ],
        per_user=True,
        per_chat=True,
    )
