#!/bin/sh

# Застосовуємо міграції
python manage.py migrate
python manage.py ensure_superuser

# Запускаємо сервер
python manage.py runserver 0.0.0.0:8000
