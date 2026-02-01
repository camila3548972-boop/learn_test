# This script is the entry point for the worker process.
# It imports the actual bot logic from bot_worker.py and runs it.

from bot_worker import run_bot

if __name__ == "__main__":
    print("Starting worker process...")
    run_bot()
