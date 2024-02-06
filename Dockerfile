FROM ubuntu:20.04 AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential zlib1g-dev && \
    apt-get install -y python3-pip && \
    pip3 install pyinstaller==6.3.0

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./ ./

CMD [ "pyinstaller", "das-cli.py", "-y", "-F", "-n", "das-cli" ]

