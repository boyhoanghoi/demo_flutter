#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
# python manage.py createsuperuser --noinput # Bỏ comment nếu bạn muốn tạo superuser tự động (cần set biến môi trường DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL)