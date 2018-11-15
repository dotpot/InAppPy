setup:
	pipenv install

clean:
	rm -rf dist build

build:
	 pipenv run python3 setup.py sdist bdist_wheel

release:
	twine upload dist/*

test:
	tox

lint:
	pipenv run flake8

rebuild: clean build
