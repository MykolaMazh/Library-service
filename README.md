# Library

A Django REST Framework API for borrowing books and pay for it using Stripe payment system.

---

## 📦 Features

-  Registration
-  JWT authentication
-  Users can borrow books, pay for it and return 
-  Interactive API documentation with Swagger
-  Admin dashboard for data management

---

## 🚀 Tech Stack

- Python 3.12+
- PostgreSQL
- drf-spectacular for API docs
- !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1Render.com for deployment!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

---

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

### 4. Create a `.env` file

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