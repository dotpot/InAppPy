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

black:
	pipenv run black --config black.toml .

lint:
	pipenv run flake8

runall: black lint test clean build

rebuild: clean build
