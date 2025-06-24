FROM ubuntu:22.04 AS builder

ENV TZ=America/Sao_Paulo \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y build-essential debhelper zlib1g-dev python3-pip python3 gzip && \
    curl -fsSL "https://github.com/tianon/gosu/releases/download/1.16/gosu-amd64" -o /usr/local/bin/gosu && \
    chmod +x /usr/local/bin/gosu

RUN pip3 install pyinstaller==6.3.0

WORKDIR /app/das

COPY . .

CMD [ "scripts/build-entrypoint.sh" ]

