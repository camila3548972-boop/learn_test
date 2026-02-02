release: python main.py
web: gunicorn web_server:app
worker: python -c 'from bot_worker import run_bot; run_bot()'