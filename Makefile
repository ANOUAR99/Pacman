NAME = pac-man.py
PYTHON = python3
CONFIG = config.json

VENV = .venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python

WHEEL = mazegenerator-00001\ \(1\)/mazegenerator-2.1.0-py3-none-any.whl

.PHONY: install run debug clean lint

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install "$(WHEEL)"

run:
	$(PYTHON_VENV) $(NAME) $(CONFIG)

debug:
	$(PYTHON_VENV) -m pdb $(NAME) $(CONFIG)

clean:
	rm -rf $(VENV)
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf __pycache__
	rm -rf src/__pycache__

lint:
	$(PYTHON_VENV) -m flake8 .
	$(PYTHON_VENV) -m mypy src/ $(NAME)
