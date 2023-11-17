FROM python:3.8-slim

RUN pip3 install --upgrade pip
RUN apt-get update

WORKDIR /app
COPY . /app

RUN pip3 install -r /app/requirements.txt
RUN pip3 install torch

CMD python3 main.py --towhee