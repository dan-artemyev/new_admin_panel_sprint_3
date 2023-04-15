FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY run_uwsgi.sh run_uwsgi.sh
COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini
COPY prepare_db_data.sh prepare_db_data.sh

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install -r requirements.txt  \
     && apt-get update  \
     && apt-get install -y netcat

COPY . .

EXPOSE 8000
RUN python manage.py collectstatic --noinput
RUN chmod +x ./prepare_db_data.sh

ENTRYPOINT ["./prepare_db_data.sh", "uwsgi", "--strict", "--ini", "uwsgi.ini"]