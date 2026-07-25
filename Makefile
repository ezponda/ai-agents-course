# Makefile for building Jupyter Books

PYTHON ?= python3
MODULE ?= n8n_no_code
BOOK_DIR := courses/$(MODULE)/book

.PHONY: install install-python-lab lab-python build clean build-n8n clean-n8n build-python clean-python help

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  install-python-lab - Install the local Python course notebook interface"
	@echo "  lab-python  - Open the Python course in JupyterLab"
	@echo "  build       - Build book (MODULE=n8n_no_code by default)"
	@echo "  clean       - Remove build artifacts"
	@echo "  build-n8n   - Build the n8n no-code book"
	@echo "  clean-n8n   - Clean the n8n no-code book"
	@echo "  build-python - Build the Python code book"
	@echo "  clean-python - Clean the Python code book"

# Install dependencies
install:
	$(PYTHON) -m pip install -r requirements.txt

# Local executable view for the Python course
install-python-lab:
	$(PYTHON) -m pip install -r courses/python_code/requirements-local.txt

lab-python:
	$(PYTHON) -m jupyter lab courses/python_code/book

# Build book (generic)
build:
	jupyter-book build $(BOOK_DIR)

# Clean build artifacts (generic)
clean:
	rm -rf $(BOOK_DIR)/_build

# n8n-specific aliases
build-n8n:
	$(MAKE) build MODULE=n8n_no_code

clean-n8n:
	$(MAKE) clean MODULE=n8n_no_code

# python-specific aliases
build-python:
	$(MAKE) build MODULE=python_code

clean-python:
	$(MAKE) clean MODULE=python_code
