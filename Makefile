install:
	python3 -m venv venv
	. venv/bin/activate
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	python manage.py runserver

test:
	python manage.py test
	
reset_migrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path './venv/*' -delete
	@if test -f "db.sqlite3"; then\
		rm db.sqlite3;\
	fi
	python manage.py makemigrations
	python manage.py migrate
