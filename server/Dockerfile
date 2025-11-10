FROM python:3.11-slim

RUN apt-get update && apt-get -y install gcc libpq-dev && apt-get clean
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src_django/ .

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8001"]
