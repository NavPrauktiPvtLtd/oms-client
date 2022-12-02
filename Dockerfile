FROM python:3.9

ENV DISPLAY=:0

WORKDIR /home

COPY requirements.txt /home

RUN apt-get update \
&& apt-get install -y vlc && apt-get install -y pulseaudio


RUN pip install -r requirements.txt

COPY . /home