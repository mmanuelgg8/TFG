# Makefile for a Python project
IMAGE_NAME = tfg

.PHONY: clean install test

# Set the default target
default: install

# Install dependencies
install:
	pip install -r requirements.txt

# Clean up temporary files
clean:
	rm -rf __pycache__ *.pyc

# Additional targets can be added based on project needs

build-image:
	docker build --no-cache -t $(IMAGE_NAME) .
	@echo y | docker container prune
	@echo y | docker image prune

run-image:
	docker run -it -v resources:/root/resources tfg python main.py -c $(FILE)

run:
	cd app && pwd && python -m main $(ARGS)

test-run:
	cd app && pwd && python -m main -c "isla_mayor.json"

venv:
	virtualenv TFG
