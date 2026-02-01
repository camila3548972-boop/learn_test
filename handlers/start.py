from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! I'm your channel helper bot.\n\n/newpost - Create a new post\n/editpost - (Coming Soon!) Edit an existing post\n/cancel - Cancel any current operation"
    )

start_handler = CommandHandler("start", start)
