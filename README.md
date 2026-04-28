# Proxy Access Service

## Описание проекта

Proxy Access Service - это сервис прокси-доступа с регистрацией пользователей, личным кабинетом и desktop-приложением для подключения к прокси-серверу с помощью одноразового ключа активации.

Проект позволяет:

- зарегистрироваться на сайте
- получить ключ активации по email
- войти в личный кабинет
- просматривать текущий ключ активации
- обновлять ключ активации
- менять пароль
- подключаться к прокси через desktop-приложение
- получать данные назначенной виртуальной машины (proxy server)
- отслеживать статус подключения через WebSocket

После регистрации пользователю автоматически генерируется одноразовый ключ активации, который отправляется на email через Celery.

При вводе ключа в desktop-приложении система проверяет его валидность и назначает свободную виртуальную машину. Если все прокси заняты — возвращается понятная ошибка.

---

## Технологии

В проекте используются:

- Python 3.12
- Django
- Django REST Framework
- SQLite
- Celery
- Redis
- Django Channels
- WebSocket
- Vue 3
- Vuetify
- Tkinter + CustomTkinter
- Docker
- Docker Compose
- Swagger / Redoc
- Pytest

---

## Инструкция по запуску

### Клонировать репозиторий

```bash
git clone git@github.com:Arina-Islibaeva/proxy-access-service.git
```

### Перейти в директорию проекта

```bash
cd proxy-access-service
```

### Настройка переменных окружения

В проекте есть файл `.env.example`, необходимо создать свой файл `.env`:

```bash
cp .env.example .env
```

После этого заполнить переменные окружения своими значениями.

### Запуск проекта через Docker

Проект запускается одной командой:

```bash
docker compose up -d --build
```

#### После запуска будут подняты:

- backend
- frontend
- redis
- celery worker
- Swagger документация

### Применение миграций

После первого запуска следует применить миграции базы данных:

```bash
docker compose exec backend python manage.py migrate
```

### Создание суперпользователя

Для доступа к Django Admin создать суперпользователя:

```bash
docker compose exec backend python manage.py createsuperuser
```

После выполнения команды нужно ввести:

- email
- пароль
- подтверждение пароля

### Django Admin

Админ-панель доступна по адресу:

http://localhost:8000/admin/

#### Swagger

http://localhost:8000/api/docs/swagger/

#### Redoc

http://localhost:8000/api/docs/redoc/

#### Как зарегистрироваться

- Перейти на страницу регистрации

http://localhost:5173/register

- Ввести

1. email
2. пароль
3. подтверждение пароля

После успешной регистрации появится сообщение:

"Письмо с ключом отправлено на почту"

#### Как получить ключ активации

После регистрации Celery запускает асинхронную задачу отправки письма с ключом активации.

Для тестирования используется console backend:

```bash
docker compose logs celery
```

В логах Celery можно увидеть письмо:

"Здравствуйте!

Ваш ключ активации: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Используйте его для подключения к прокси-серверу.
"

Быстрее и удобнее скопировать ключ активации в личном кабинете:

http://localhost:5173/profile

### Как запустить desktop-приложение

Desktop-приложение находится в папке:

desktop/

#### Установка зависимостей

```bash
cd desktop
```

```bash
pip install -r requirements.txt
```

### Запуск приложения

```bash
python proxy_app.py
```

---

# Автор

Арина Ислибаева

Ссылка на GitHub:

https://github.com/Arina-Islibaeva
