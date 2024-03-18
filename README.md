# "Продуктовый помощник" (Foodgram)

## 1. Описание <a id=1></a>

Проект "Продуктовый помошник" (Foodgram) - сайт, на котором пользователи могут: 
  - регистрироваться
  - создавать свои рецепты и управлять ими (корректировать\удалять)
  - просматривать рецепты других пользователей
  - добавлять рецепты других пользователей в "Избранное" и в "Список покупок"
  - подписываться на других пользователей
  - скачать список ингредиентов для рецептов, добавленных в "Список покупок"

---
## 2. База данных и переменные окружения <a id=3></a>

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения.

Шаблон для заполнения файла ".env":
```python
SECRET_KEY='Здесь указать секретный ключ'
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

---
## 3. Команды для локального запуска <a id=4></a>

Перед запуском необходимо склонировать проект:
```bash
git clone git@github.com:kekul78/foodgram-project-react.git

```

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Далее можно создавать и запускать контейнеры. 
Из корневой папки выполнить команду:
```bash
docker-compose up
```

Или же запустить как демона:
```bash
docker-compose up -d
```

После успешного запуска контейнеров выполнить миграции:
```bash
docker-compose exec backend python manage.py migrate
```

Создать суперюзера (Администратора):
```bash
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```bash
docker-compose exec backend python manage.py collectstatic
```

Теперь доступность проекта можно проверить по адресу [http://localhost/](http://localhost/)

---
## 4. Сайт <a id=8></a>

Адрес сайта: [foodgram.ddnsking.com](https://foodgram.ddnsking.com)
