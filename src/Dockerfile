FROM ubuntu

LABEL Tjarko Tjaden <t.tjaden@fz-juelich.de>

RUN apt-get update
RUN apt-get install -y python3 python3-pip

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY ./ /vdi-4657-3-webtool
WORKDIR /vdi-4657-3-webtool

CMD gunicorn --bind 0.0.0.0:80 --workers=4 wsgi