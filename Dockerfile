FROM python:3.9-slim

LABEL maintainer "Tjarko Tjaden, t.tjaden@gmail.com"

# set working directory in container
WORKDIR /usr/src/app

# copy and install packages
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# copy app folder to app folder in container
COPY /src /usr/src/app/

# changing to non-root user
RUN useradd -m appUser
USER appUser

# Run locally
CMD gunicorn -b 0.0.0.0:8050 app:server
