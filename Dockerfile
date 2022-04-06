FROM python:latest

WORKDIR /src
COPY requirements.txt /src
RUN sudo pip install -r requirements.txt
COPY . /src