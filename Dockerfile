FROM python:3.9-alpine

WORKDIR /home/lcdui
RUN apk add --no-cache i2c-tools libgpiod-dev gcc libc-dev g++ zlib-dev libjpeg-turbo-dev
RUN apk add --no-cache wiringpi-dev
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv install --system
COPY . .

USER 1337:1337
ENTRYPOINT [ "python3", "lcd_ui.py"]
