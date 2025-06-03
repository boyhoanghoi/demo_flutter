#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip # Thêm dòng này (tùy chọn)

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
