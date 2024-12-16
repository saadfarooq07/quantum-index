.PHONY: build run clean test lint

build:
	docker-compose build

run:
	docker-compose up

dev:
	docker-compose up --build

clean:
	docker-compose down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

test:
	docker-compose run --rm ide python -m pytest

lint:
	docker-compose run --rm ide black .
	docker-compose run --rm ide isort .

shell:
	docker-compose run --rm ide /bin/bash
