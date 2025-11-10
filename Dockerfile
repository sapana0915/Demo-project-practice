FROM python:3.12.2
ENV ENV=prod
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install "drf-yasg[validation]"
RUN pip install git+https://github.com/atomic-loops/atomicloops-django-logger
WORKDIR /opt/
