FROM python:3.11.7-slim

ARG APP_VERSION

RUN apt-get update && apt-get install -y \
    make \
    curl \
    gcc \
    libc-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

WORKDIR /root/app

COPY app /root/app
COPY resources /root/resources
COPY data /root/data

# CMD ["python", "main.py"]
