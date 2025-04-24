FROM python:3.11.5-alpine

WORKDIR /app

# ???
ENV DATABASE_URI=''

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "main:app"]
