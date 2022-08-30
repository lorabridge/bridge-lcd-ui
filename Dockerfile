FROM python:3.9-alpine

WORKDIR /home/lcdui
RUN apk add i2c-tools libgpiod-dev gcc libc-dev g++
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system
COPY . .

USER 1337:1337
ENTRYPOINT [ "python3", "lcd-ui.py"]
