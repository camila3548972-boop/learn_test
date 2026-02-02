import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Required Environment Variables ---
# Use 'TOKEN' to match Railway environment variables. 
# This will read the variable directly from the Railway dashboard.
TOKEN = os.getenv("TOKEN") 
CHANNEL_ID = os.getenv("CHANNEL_ID")

# --- Optional Environment Variables ---
# For the /invite command
INVITE_LINK = os.getenv("INVITE_LINK", "https://t.me/your_channel_invite_link")

# --- Bot Configuration ---
# A unique tag to identify messages posted by this bot, for editing purposes.
BOT_POST_TAG = "#post_by_channel_bot"
LIVESTREAM_MESSAGE_TAG = "#livestream_by_channel_bot" # Tag for livestream announcements

# Categories for the /newpost command
CATEGORIES = ["📢 Announcement", "📰 News", "✨ Update", "💡 Tip"]

# --- Conversation States ---
# We define the states for each conversation handler as numerical constants.
# Using a range for each handler helps keep them organized.

# new_post_handler states (0-9)
SELECTING_CATEGORY, TYPING_TYPE, TYPING_DETAILS, AWAITING_MEDIA, ASKING_BUTTONS, TYPING_BUTTONS = range(6)

# edit_post_handler states (10-19)
SELECTING_POST_TO_EDIT, EDITING_POST, AWAITING_NEW_CAPTION = range(10, 13)

# dm_handler states (20-29)
AWAITING_DM_USER_ID, AWAITING_DM_MESSAGE = range(20, 22)

# livestream_handler states (30-39)
SELECTING_LIVESTREAM_ACTION, AWAITING_LIVESTREAM_TITLE, AWAITING_LIVESTREAM_LINK = range(30, 33)

# restrict_user_handler states (40-49)
AWAITING_RESTRICT_USER_ID = 40

# admin_panel_handler state (50-59)
ADMIN_PANEL = 50

