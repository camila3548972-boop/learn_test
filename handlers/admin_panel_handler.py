from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext

# Define the admin panel command handler
def admin_panel_command(update: Update, context: CallbackContext) -> None:
    """Displays the admin panel with action buttons."""
    keyboard = [
        [InlineKeyboardButton("📝 New Post", callback_data='admin_new_post')],
        [InlineKeyboardButton("✏️ Edit Post", callback_data='admin_edit_post')],
        [InlineKeyboardButton("🔒 Restrict User", callback_data='admin_restrict_user')],
        [InlineKeyboardButton("💬 DM User", callback_data='admin_dm_user')],
        [InlineKeyboardButton("🔴 Start Livestream", callback_data='admin_start_livestream')],
        # This button will now instruct the user on how to use the /invite command
        [InlineKeyboardButton("✉️ Invite User", callback_data='admin_instruct_invite')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🔐 Admin Panel", reply_markup=reply_markup)

# Define a new callback function for the invite instruction
async def instruct_invite(update: Update, context: CallbackContext) -> None:
    """Informs the admin how to use the /invite command."""
    query = update.callback_query
    await query.answer() # Acknowledge the button press
    await query.message.reply_text(
        "To invite a user, please use the following command format:\n"
        "`/invite <user_id>`\n\n"
        "Replace `<user_id>` with the numerical ID of the user you want to invite."
    )

# Create the CommandHandler for the /admin command
def admin_panel_handler() -> CommandHandler:
    return CommandHandler('admin', admin_panel_command)
