up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f airflow

lint:
	ruff check .

test:
	pytest -q
