run:
	uvicorn config.app:app --port 8000 --reload

migrations:
	alembic revision --autogenerate -m '$(message)'

migrate:
	alembic upgrade head

run_dev:
	poetry run alembic upgrade head
	poetry run uvicorn config.app:app --host 0.0.0.0 --reload --workers 3

up:
	sudo docker compose up --build

down:
	sudo docker compose down
