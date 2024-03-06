# Makefile for a Python project
IMAGE_NAME = image-pipeline

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

# build-image:
# 	docker build --no-cache -t $(IMAGE_NAME) .
# 	@echo y | docker container prune
# 	@echo y | docker image prune

build-image:
	docker compose build $(IMAGE_NAME)
	docker compose up

build-image-no-cache:
	docker compose build --no-cache $(IMAGE_NAME)
	docker compose up

# run-image:
# 	docker run -it -v resources:/root/resources $(IMAGE_NAME) python main.py -c $(FILE)

run-image:
	docker compose run --rm $(IMAGE_NAME) python main.py -c $(FILE)

image-ssh:
	docker compose run --rm $(IMAGE_NAME) /bin/bash

run:
	cd app && pwd && python -m main $(ARGS)

test-run:
	cd app && pwd && python -m main -c "isla_mayor.json"

venv:
	virtualenv TFG
