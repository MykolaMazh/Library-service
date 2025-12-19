# Library

A Django REST Framework API for borrowing books and pay for it using Stripe payment system.

---

## 📦 Features

-  Registration
-  JWT authentication
-  Users can borrow books, pay for it and return
-  Ones borrowings or payments has been created a notification is sent to telegram chat so if the payment has not been 
   paid
-  Interactive API documentation with Swagger
-  Admin dashboard for data management

---

***Create a Telegram bot***

1. Open Telegram and message **@BotFather**.
  
2. Use `/newbot` → follow prompts → you’ll receive a **bot token** like:
  
  `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`

  ---

***Create a Telegram chat***

- Create a private group or channel for notifications.
- Add your bot to that chat and **promote it as an admin** (so it can send messages).
- Use this method to get the **chat ID**:
  
  - Visit:
    
    `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates`
    
  - Send a test message in the chat.
    
  - The response JSON will contain a `"chat":{"id":<TELEGRAM_CHAT_ID>}` value.
  
From [Stripe](https://dashboard.stripe.com/login) get your STRIPE_SECRET_KEY and
STRIPE_PUBLISHABLE_KEY.

These variables should be in `.env` file.


## 🔑 Authentication

This project uses **JWT authentication** via `/api/users/token/` after registration on `/api/users/register/`.   
`Authorithation` header is replaced with `Authiorize`.

## 📄 API Documentation

- Documentation for endpoints is provided by Swagger UI using `drf-spectacular`: url -`/api/doc/`



## Run in Docker
create `docker-compose.yml`
```yaml
services:
  library-service:
    image: nick098/library-service:postgres_dev
    ports:
      - "8080:8080"
    command: >
      sh -c "python manage.py wait_for_db &&
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8080"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: postgres:14-alpine
    ports:
      - "5432:5432"
    env_file:
      - .env
    volumes:
      - my_db:/var/lib/postgresql/data

  celery-worker:
    image: nick098/celery-worker:postgres_dev
    command: celery -A library_service worker -l info
    env_file:
      - .env
    depends_on:
      - db
      - redis
      - library-service

  celery-beat:
    image: nick098/celery-beat:postgres_dev
    command: celery -A library_service beat -l info
    env_file:
      - .env
    depends_on:
      - db
      - redis
      - library-service

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  my_db:

```
then pull and up
```bash
docker compose pull
docker compose up
```
stop containers
```bash
docker compose stop
```

### Create a `.env` file from `sample.env`

settings.py is split into prod.py and dev.py so

for development `.env`

```ini
DJANGO_SETTINGS_MODULE=library_service.settings.dev
```

fo production `.env`

```ini
DJANGO_SETTINGS_MODULE=library_service.settings.prod
```

copy .env file to  application container

```bash
 docker cp .env <your_name_for_library-service_container>:/app/
```

start containers
```bash
docker compose start
```

Create a superuser

```bash
docker compose exec -it library-service bash
```
tests
```bash
docker compose exec -it library-service python manage.py test
```