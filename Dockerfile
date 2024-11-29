FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    jq \
    gnupg \
    && rm -rf /var/lib/apt/lists/*
# Google Chromeのインストール
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*
# ChromeDriver(ver115以降)の最新のStableバージョンをダウンロードし、/app/code/にインストールする
RUN LATEST_VERSION=$(wget -qO- https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.version') \
    && DOWNLOAD_URL=$(wget -qO- https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64").url') \
    && wget -O /tmp/chromedriver.zip $DOWNLOAD_URL \
    && unzip /tmp/chromedriver.zip -d /app/code/ \
    && rm /tmp/chromedriver.zip \
    && mv /app/code/chromedriver-linux64/chromedriver /app/code/chromedriver \
    && rm -rf /app/code/chromedriver-linux64 \
    && chmod +x /app/code/chromedriver

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
