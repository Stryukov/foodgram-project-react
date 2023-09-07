FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install gunicorn==20.1.0

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
COPY ./entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]