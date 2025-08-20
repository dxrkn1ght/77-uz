.PHONY: help install migrate test coverage translations admin setup

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  migrate      - Run database migrations"
	@echo "  test         - Run tests"
	@echo "  coverage     - Run tests with coverage"
	@echo "  translations - Update translation files"
	@echo "  admin        - Create admin user and sample data"
	@echo "  setup        - Full project setup"

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	python manage.py test

coverage:
	coverage run --source='.' manage.py test
	coverage report --show-missing
	coverage html

translations:
	python manage.py makemessages -l uz
	python manage.py makemessages -l ru
	python manage.py compilemessages

admin:
	python manage.py setup_admin

setup: install migrate translations admin
	@echo "Project setup completed!"
	@echo "Admin user: +998901234567 / admin123"
	@echo "Run: python manage.py runserver"

