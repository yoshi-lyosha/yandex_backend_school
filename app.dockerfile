FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-alpine3.8

COPY ./ /app
WORKDIR /app/

RUN apk update && apk add gcc python3-dev musl-dev

RUN pip install -r /app/requirements.txt
ENV PYTHONPATH=/app

EXPOSE 80
