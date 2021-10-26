FROM amsterdam/python

LABEL maintainer=datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y
RUN pip install --upgrade pip
RUN pip install uwsgi

COPY /app /app
COPY /tests /app/tests
COPY /requirements.txt /app
COPY /uwsgi.ini /app

COPY test.sh /app
COPY .flake8 /app

RUN pip install --no-cache-dir -r /app/requirements.txt

#ENTRYPOINT ["uwsgi"]
CMD uwsgi --ini /app/uwsgi.ini