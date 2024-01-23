# Makefile for a Python project

.PHONY: clean install test

# Set the default target
default: install

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	pytest

# Clean up temporary files
clean:
	rm -rf __pycache__ *.pyc

# Additional targets can be added based on project needs

run:
	cd app && pwd && python -m main

venv:
	virtualenv TFG
