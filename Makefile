# default makefile target
all::


.PHONY: help
help:
	echo "clean       - removes all untracked files"
	echo "lint        - run flake8"
	echo "package     - create package for pypi"
	echo "setup       - install project and maintainer dependencies"
	echo "test        - run tests"
	echo "upload      - create and upload distribution for pypi"
	echo "upload-test - create and upload distribution for testpypi"

.PHONY: clean
clean:
	git clean -fxd

.PHONY: upload
upload: package
	python -m twine upload --repository nasdaq-data-link --non-interactive dist/*

.PHONY: upload-test
upload-test: package
	python -m twine upload --repository test-nasdaq-data-link --non-interactive --verbose dist/*

.PHONY: lint
lint:
	flake8

.PHONY: package
package: clean
	python setup.py sdist bdist_wheel

.PHONY: setup
setup:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install setuptools wheel twine
	pip install flake8
	pip install tox

.PHONY: test
test:
	tox
