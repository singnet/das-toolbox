FROM ubuntu:22.04 AS builder

ENV TZ=America/Sao_Paulo \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    debhelper \
    zlib1g-dev \
    python3-pip \
    python3 \
    gzip \
    git \
    uuid-runtime \
    patchelf

RUN curl -fsSL https://get.docker.com/ | bash

RUN pip3 install pyinstaller==6.3.0

WORKDIR /app/das

COPY . .

ENTRYPOINT [ "make" ]
CMD [ "build-local" ]

