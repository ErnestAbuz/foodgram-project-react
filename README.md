[![Django-app workflow](https://github.com/f0rt3hlulz/foodgram-project-react/actions/workflows/foodgram_forkflow.yml/badge.svg)](https://github.com/f0rt3hlulz/foodgram-project-react/actions/workflows/foodgram_forkflow.yml)

# Описание.

Проект «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Стек: Python 3, Django 3, Django REST Framework, SQLite3, PostgreSQL, gunicorn, nginx, Яндекс.Облако (Ubuntu 22.04)

# Особенности
Проект запускается в четырёх контейнерах [docker-compose](https://docs.docker.com/compose/install/)

IMAGES            | NAMES             | DESCRIPTIONS
------------------|-------------------|--------------------------------------------
nginx:1.19.3      | infra_nginx_1     | контейнер HTTP-сервера
postgres:12.4     | infra_db_1        | контейнер базы данных на PostgreSQL
foodgram_backend  | infra_web_1       | контейнер backend-части Django приложения
foodgram_frontend | infra_frontend_1  | контейнер frontend-части проекта JS-React

_*Примечание: При выполнении команды ```docker-compose up``` сервис frontend подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу и будет работать через ```nginx```._

# Запуск и работа с проектом
Чтобы развернуть проект, вам потребуется:
1) Клонировать репозиторий GitHub (не забываем создать виртуальное окружение и установить зависимости):
```python
git clone https://github.com/f0rt3hlulz/foodgram-project-react
```
2) Создать файл ```.env``` в папке проекта _/infra/_ и заполнить его всеми ключами:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=f00dgram
DB_HOST=db
DB_PORT=5432
DJANGO_SECRET_KEY=<ваш_django_секретный_ключ>
```

3) Собрать контейнеры:
```python
cd foodgram-project-react/infra
docker-compose up -d --build
```
При успешном создании контейнеров в терминале должен быть статус:
```
    Status: Downloaded newer image for nginx:1.19.3
    Creating infra_db_1       ... done
    Creating infra_web_1      ... done
    Creating infra_nginx_1    ... done
```

4) Сделать миграции, собрать статику и создать суперпользователя:
```python
docker-compose exec -T web python manage.py makemigrations users --noinput
docker-compose exec -T web python manage.py makemigrations recipes --noinput
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --no-input
docker-compose exec web python manage.py createsuperuser
```

Чтобы заполнить базу данных начальными данными списка ингридиетов выполните:
```python
docker-compose exec -T web python manage.py loaddata data/ingredients.json 
```
Теперь можно зайти в админку _http://<ваш хост>/admin/_ под вашим логином администратора.

## Регистрация и авторизация
В сервисе предусмотрена система регистрации и авторизации пользователей.
Обязательные поля для пользователя:
<li> Логин
<li> Пароль
<li> Email
<li> Имя
<li> Фамилия

## Права доступа к ресурсам сервиса

### неавторизованные пользователи могут:

    - создать аккаунт;
    - просматривать рецепты на главной;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;

### авторизованные пользователи могут:

    - входить в систему под своим логином и паролем;
    - выходить из системы (разлогиниваться);
    - менять свой пароль;
    - создавать/редактировать/удалять собственные рецепты;
    - просматривать рецепты на главной;
    - просматривать страницы пользователей;
    - просматривать отдельные страницы рецептов;
    - фильтровать рецепты по тегам;
    - работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов;
    - работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок;
    - подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок;

### администратор
Администратор обладает всеми правами авторизованного пользователя.
<br> Плюс к этому он может:

    - изменять пароль любого пользователя;
    - создавать/блокировать/удалять аккаунты пользователей;
    - редактировать/удалять любые рецепты;
    - добавлять/удалять/редактировать ингредиенты;
    - добавлять/удалять/редактировать теги.

# Админка
В интерфейс админ-зоны выведены следующие поля моделей и фильтры:
### Модели:
    Доступны все модели с возможностью редактирования и удаления записей.

### Модель пользователей:
    Фильтр по email и имени пользователя.

### Модель рецептов:
    В списке рецептов доступны название и авторы рецептов.
    Фильтры по автору, названию рецепта, тегам.
    Выведена информация о популярности рецепта: общее число добавлений этого рецепта в избранное пользователей.

### Модель ингредиентов:
    В списке ингредиентов доступны название ингредиента и единицы измерения.
    Фильтр по названию.

# Ресурсы сервиса

### Рецепт
Рецепт описывается полями:

    Автор публикации (пользователь).
    Название рецепта.
    Картинка рецепта.
    Текстовое описание.
    Ингредиенты: продукты для приготовления блюда по рецепту с указанием количества и единиц измерения.
    Тег.
    Время приготовления в минутах.

### Тег
Тег описывается полями:

    Название.
    Цветовой HEX-код.
    Slug.

### Ингредиент
Ингредиент описывается полями:

    Название.
    Количество (только для рецепта).
    Единицы измерения.

### Список покупок.
Список покупок скачивается в текстовом формате: shopping-list.txt.

## Фильтрация по тегам
При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам в комбинации «или»: если выбраны несколько тегов — в результате должны быть показаны рецепты, которые отмечены хотя бы одним из этих тегов.
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. Такой же принцип соблюдается при фильтрации списка избранного.

# Примеры запросов к API.

Запросы к API начинаются с «/api/v1/»

1) регистрация пользователя

POST-запрос: /api/users/
<br /> *Request sample:*
```python
{

    "email": "string",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "password": "string"

}
```
*Response sample (201):*
```python
{

    "email": "string",
    "id": 0,
    "username": "string",
    "first_name": "string",
    "last_name": "string"

}
```
*Response sample (400):*
```python
{
    «field_name»: [
      «Обязательное поле.»
    ]
}
```

2) Получение токена

POST-запрос: /api/auth/token/login/
<br /> *Request sample:*
```python
{
    «email»: «string»,
    «password»: «string»
}
```
*Response sample (201):*
```python
{
    «token»: «string»
}
```
*Response sample (400):*
```python
{
    «field_name»: [
      «string»
    ]
}
```

