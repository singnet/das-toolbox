FROM ubuntu:20.04 AS builder-binary

WORKDIR /app

RUN apt-get update && \
    apt-get install -y build-essential zlib1g-dev python3-pip && \
    pip3 install pyinstaller==6.3.0

COPY ./src/requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./src ./

RUN pyinstaller das-cli.py -y -F -n das-cli

FROM ubuntu:20.04 AS builder-deb-package

WORKDIR /tmp/das-cli

COPY ./DEBIAN/ ./package/DEBIAN/

COPY --from=builder-binary /app/dist/das-cli ./package/usr/local/bin/

ENTRYPOINT [ "dpkg-deb" ]
CMD [ "-b", "./package", "./dist"]
