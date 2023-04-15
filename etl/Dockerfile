FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get update \
    && apt-get install -y netcat

COPY . .

ENTRYPOINT ["python", "main.py"]
