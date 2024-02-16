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

build-image:
	docker build --no-cache -t tfg .

run-image:
	docker run -it -v resources:/root/resources tfg python main.py -c $(FILE)

run:
	cd app && pwd && python -m main $(ARGS)

download:
	cd app && pwd && python -m main --download $(ARGS)

train:
	cd app && pwd && python -m main --train $(ARGS)

test-run:
	cd app && pwd && python -m main \
		--bands "B04" "B08" \
    --formula "NDVI" \
    --bbox -6.215864855019264 37.162534357525814 -6.111682075391747 37.10259292740977 \
    --evalscript "ndvi" \
    --start_date "2017-01-01" \
    --end_date "2022-01-01" \
    --interval_type "weeks" \
    --date_interval 1 \
		--name_id "islamayor_ndvi" \
		--download \
		--train \
		--models "random_forest" "arima" \
		$(ARGS)

test-download:
	cd app && pwd && python -m main \
		--bands "B04" "B08" \
		--formula "NDVI" \
		--bbox -6.215864855019264 37.162534357525814 -6.111682075391747 37.10259292740977 \
		--evalscript "ndvi" \
		--start_date "2017-01-01" \
		--end_date "2022-01-01" \
		--interval_type "weeks" \
		--date_interval 1 \
		--name_id "islamayor_ndvi" \
		--download \
		$(ARGS)

test-train:
	cd app && pwd && python -m main \
		--bands "B04" "B08" \
		--formula "NDVI" \
		--start_date "2017-01-01" \
		--interval_type "weeks" \
		--date_interval 1 \
		--name_id "islamayor_ndvi" \
		--models "random_forest" "arima" \
		--train \
		$(ARGS)

venv:
	virtualenv TFG
