import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates a one-time invite link for the channel."""
    if not context.args:
        await update.message.reply_text("Please provide a user ID. Usage: /invite <user_id>")
        return

    try:
        user_id_to_invite = int(context.args[0])
        chat_id = os.getenv("CHANNEL_ID")

        # Create an invite link that is specific to the user and expires after one use.
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=chat_id,
            name=f"Invite for user {user_id_to_invite}",
            member_limit=1,
        )

        # Send the invite link to the user who requested it.
        await update.message.reply_text(
            f"Here is the one-time invite link for user {user_id_to_invite}:\n"
            f"{invite_link.invite_link}"
        )

    except (ValueError, IndexError):
        await update.message.reply_text("Invalid user ID. Please provide a numeric user ID.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")


def invite_handler() -> CommandHandler:
    """Creates a CommandHandler for the /invite command."""
    return CommandHandler("invite", invite)
