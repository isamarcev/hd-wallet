run:
	uvicorn config.app:app --port 8000 --reload

migrations:
	alembic revision --autogenerate -m '$(message)'

migrate:
	alembic upgrade head
