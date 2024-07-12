FROM python:3.10

WORKDIR /app

COPY main.py /app
COPY .env /app
COPY requirements.txt /app

# Install necessary packages
RUN apt-get update \
    && apt-get install -y wget unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y firefox-esr \
    && rm -rf /var/lib/apt/lists/*
RUN wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    && tar -C /usr/local/bin/ -xzf /tmp/geckodriver.tar.gz \
    && rm /tmp/geckodriver.tar.gz

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
