release: python -c "from src.models import init_db; init_db()"
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
