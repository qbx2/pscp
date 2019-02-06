PYTHON ?= python

all:
	$(PYTHON) setup.py build sdist

install:
	$(PYTHON) setup.py install

clean:
	$(PYTHON) setup.py clean --all

test:
	$(PYTHON) setup.py test

pytest:
	pytest tests.py
