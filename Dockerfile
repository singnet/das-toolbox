FROM ubuntu:20.04 AS builder

ENV TZ=America/Sao_Paulo \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential debhelper zlib1g-dev python3-pip python3

WORKDIR /app/das

COPY . .

CMD ["make", "build"]

