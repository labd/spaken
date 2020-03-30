.PHONY: install release coverage clean

clean:
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

install:
	pip install -e .

test:
	pytest

format:
	isort --recursive src tests
	black src/ tests/

coverage:
	py.test --cov=spaken --cov-report=term-missing --cov-report=html

release:
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload dist/*
