release: python main.py
web: gunicorn wsgi:app --timeout 120
worker: python -c 'from bot_worker import run_bot; run_bot()'