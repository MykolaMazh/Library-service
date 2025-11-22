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

## 🚀 Tech Stack

- Python 3.12+
- PostgreSQL
- drf-spectacular for API docs
- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1Render.com for deployment!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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

## ⚙️ Local Setup

### 1. Clone the project

```bash
git clone https://github.com/MykolaMazh/Library-service.git

```

### 2. Create and activate a virtual environment

```bash
python -m venv venv 
source venv/bin/activate # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file from `sample.env`

settings.py is split into prod.py and dev.py so

for development `.env`

```ini
DJANGO_SETTINGS_MODULE=library_service.settings.dev
```

fo production `.env`

```ini
DJANGO_SETTINGS_MODULE=library_service.settings.prod
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run the server

```bash
python manage.py runserver
```

## 🔑 Authentication

This project uses **JWT authentication** via `/api/users/token/` after registration on `/api/users/register/`.

## 📄 API Documentation

- Documentation for endpoints is provided by Swagger UI using `drf-spectacular`: url -`/api/doc/`

### Tests

```ini
python manage.py test
```

## Run in Docker
create `docker-compose.yml`
```yaml
services:
  library-service:
    image: nick098/library-service:latest
    ports:
      - "8080:8080"
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
    image: nick098/celery-worker:latest
    env_file:
      - .env
    depends_on:
      - db
      - redis
      - library-service

  celery-beat:
    image: nick098/celery-beat:latest
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
then pull and run
```bash
docker compose pull
docker compose up
```
tests
```bash
docker compose exec library-service python manage.py test
```

### App in production on `render.com` connected to PostgreSQL - `https://social-media-api-rx5z.onrender.com`