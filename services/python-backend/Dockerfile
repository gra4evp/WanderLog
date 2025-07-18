FROM python:3.12-slim

# install some basic utilities
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        ffmpeg \
        libsm6 \
        libxext6 \
        libgl1 \
        libxrender1 \
        libx11-6 \
        libxtst6 \
        wget \
        curl \
        unzip \
        ca-certificates \
        fonts-liberation \
        && \
    rm -rf /var/lib/apt/lists/*

# create venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# update pip
RUN pip3 install --upgrade pip ;\
    pip3 install setuptools

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . /app/
