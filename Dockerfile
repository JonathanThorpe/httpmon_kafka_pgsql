FROM python:3.7-alpine

#Install build dependencies - see https://github.com/docker-library/python/issues/312
RUN apk add --no-cache --virtual .build-deps gcc musl-dev
COPY . /app
WORKDIR /app
RUN pip install .

#Remove build dependencies to keep the image size small
RUN apk del .build-deps
CMD httpmon-kafka-pgsql