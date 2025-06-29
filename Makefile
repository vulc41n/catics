install:
	python3 -m venv venv
	. venv/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt
	venv/bin/python manage.py migrate

run:
	venv/bin/python manage.py runserver

run_prod:
	venv/bin/gunicorn catics.wsgi

test:
	python manage.py test
	
reset_migrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path './venv/*' -delete
	@if test -f "db.sqlite3"; then\
		rm db.sqlite3;\
	fi
	python manage.py makemigrations
	python manage.py migrate
