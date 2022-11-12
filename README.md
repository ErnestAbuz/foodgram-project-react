# Cервис Foodgram
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Для удобного поиска рецептов предусмотрена фильтрация по тегам.

## Стек
- Django 3.2.15
- Docker 20.10.17
- Docker-compose 2.10.2
- Gunicorn
- Nginx 1.19.3
- PostgreSQL 13.0
- django-colorfield 0.7.2
- django-filter 22.1
- Django REST framework 3.14.0
- Simple JWT 4.8.0
- djoser 2.1.0

## Запуск и работа с проектом

1. Клонируем репозиторий:
```
git clone git@github.com:ErnestAbuz/foodgram-project-react.git
```

2. Устанавливаем [Docker](https://docs.docker.com/engine/install/) (если отсутствует)

3. В директории infra/ создаем файл .env и заполняем переменными окружения по принципу как в .env.example

4. Cоздаем и активируем виртуальное окружение:

Для Mac или Linux:
```
python3 -m venv venv
source venv/bin/activate
```
Для Windows:
```
python -m venv venv
source venv/Scripts/activate
```

5. Установим зависимости из файла requirements.txt:
```
cd backend/
pip install -r requirements.txt
```

6. Собираем контейнеры:
```
cd infra/
docker-compose up -d --build
```

7. Выполняем миграции, создаем суперпользователя, собираем статику:
```
docker-compose exec -T backend python manage.py makemigrations users --noinput
docker-compose exec -T backend python manage.py makemigrations recipes --noinput
docker-compose exec -T backend python manage.py migrate --noinput
docker-compose exec backend python manage.py createsuperuser
docker-compose exec -T backend python manage.py collectstatic --no-input
```

8. Загружаем список ингредиентов в базу данных:
```
docker-compose exec backend python manage.py add_ingredients
```

9. Войдем в [панель администратора](http://localhost/admin/), создаем несколько тегов и рецептов.

10. Для остановки проекта используем:
```
docker-compose down -v 
```
