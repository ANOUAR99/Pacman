NAME = pac-man.py
PYTHON = python3
CONFIG = config.json

VENV = .venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python

all: run

install: requirements.txt
	@if [ ! -d "$(VENV)" ] || [ requirements.txt -nt "$(VENV)" ]; then \
		echo "Installing dependencies quietly... (This may take a moment)"; \
		$(PYTHON) -m venv $(VENV); \
		$(PIP) install -q --upgrade pip; \
		$(PIP) install -q -r requirements.txt; \
		touch $(VENV); \
	else \
		echo "Packages are up to date."; \
	fi

run: install
	@echo "Starting Pac-Man..."
	$(PYTHON_VENV) $(NAME) $(CONFIG)

debug: install
	$(PYTHON_VENV) -m pdb $(NAME) $(CONFIG)

clean:
	@echo "Sweeping cache files..."
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} +

lint: install
	@echo "Running Flake8..."
	@$(PYTHON_VENV) -m flake8 src/
	@echo "Running Mypy..."
	@$(PYTHON_VENV) -m mypy --warn-return-any\
	 --warn-unused-ignores --ignore-missing-imports\
	  --disallow-untyped-defs --check-untyped-defs\
	  --follow-imports=skip src/

fclean: clean
	@echo "Sweeping virtual environment..."	
	@rm -rf $(VENV)

re: fclean all

.PHONY: all install run debug clean lint lint-strict fclean re