FROM python:3.11.5-slim

WORKDIR /app

ENV DB_HOST='0.0.0.0'
ENV DB_PORT=8000

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
