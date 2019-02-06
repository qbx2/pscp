PYTHON ?= python

all:
	$(PYTHON) setup.py build sdist

install:
	$(PYTHON) setup.py install

clean:
	$(PYTHON) setup.py clean --all

test:
	flake8 pscp tests.py
	$(PYTHON) setup.py test

pytest:
	flake8 pscp tests.py
	pytest tests.py
