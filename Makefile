NAME = pac-man.py
PYTHON = python3
CONFIG = config.json

VENV = .venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python

all: run

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: install
	@echo "Starting Pac-Man..."
	$(PYTHON_VENV) $(NAME) $(CONFIG)

debug: install
	$(PYTHON_VENV) -m pdb $(NAME) $(CONFIG)

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +

lint: install
	@echo "Running Flake8..."
	$(PYTHON_VENV) -m flake8 .
	@echo "Running strict Mypy..."
	$(PYTHON_VENV) -m mypy --warn-return-any\
	 --warn-unused-ignores --ignore-missing-imports\
	  --disallow-untyped-defs --check-untyped-defs .

lint-strict: install
	$(PYTHON_VENV) -m flake8 .
	$(PYTHON_VENV) -m mypy --strict .

fclean: clean
	rm -rf $(VENV)

re: fclean all

.PHONY: all install run debug clean lint lint-strict fclean re