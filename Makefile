install:
	pip install -r requirements.txt
	python manage.py importdata	

test:
	python manage.py test	

run:
	python manage.py runserver
