FROM python:3

# Install Firefox and Webdriver
RUN apt-get update && apt-get install -y firefox-esr wget && \
    wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux64.tar.gz && \
    tar -C /usr/local/bin/ -xzf /tmp/geckodriver.tar.gz && \
    rm -f /tmp/geckodriver.tar.gz

# Install the Google SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get install apt-transport-https ca-certificates gnupg curl -y &&\
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - &&\
    apt-get update && apt-get install google-cloud-sdk -y

# Change current directory to /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code to app/
COPY . .

# CMD is called on `docker run` ; It runs the Python script and copies the resulting CSV to a cloud storage bucket.
CMD ["sh", "-c", "python scraper.py && gsutil cp ./output/*.csv gs://{your_cloud_storage_bucket}"]