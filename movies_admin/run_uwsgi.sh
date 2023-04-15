#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

uwsgi --strict --ini /etc/movies_admin/uwsgi.ini
