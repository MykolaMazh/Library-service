FROM python:3.12-slim
LABEL maintainer='mykm3ua@gmail.com'
ENV PYTHONUNBUFFERED=1
WORKDIR app/
COPY . .
RUN pip install -r requirements.txt
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
