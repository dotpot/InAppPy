clean:
	rm -rf dist build

build:
	 python3 setup.py sdist bdist_wheel

release:
	twine upload dist/*

test:
	tox

rebuild: clean build