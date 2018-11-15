FROM amsterdam/docker_python:latest

MAINTAINER datapunt@amsterdaml.nl

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install --no-cache-dir -r requirements.txt

COPY /api /app

ENTRYPOINT ["python"]

CMD ["server.py"]