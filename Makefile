# Makefile for building Jupyter Books

PYTHON ?= python3
MODULE ?= n8n_no_code
BOOK_DIR := courses/$(MODULE)/book

.PHONY: install build clean build-n8n clean-n8n help

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  build       - Build book (MODULE=n8n_no_code by default)"
	@echo "  clean       - Remove build artifacts"
	@echo "  build-n8n   - Build the n8n no-code book"
	@echo "  clean-n8n   - Clean the n8n no-code book"

# Install dependencies
install:
	$(PYTHON) -m pip install -r requirements.txt

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
