# Main web application (FastAPI)
web: gunicorn ai_os.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

# Alternative: Run the main application
# web: python main.py

# Worker for background tasks (if using Celery)
# worker: celery -A assistant_core.daemon.celery_app worker --loglevel=info
