FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install manage-fastapi

COPY requirements.txt requirements.txt

COPY . .

RUN pip3 install -r requirements.txt

# COPY . .

CMD fastapi run