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
    patchelf \
    libssl-dev \
    libglib2.0 \
    libevent-dev \
    cmake

RUN curl -fsSL https://get.docker.com/ | bash

RUN pip3 install pyinstaller==6.3.0

WORKDIR /tmp

RUN curl -L -o mongo-cxx-driver-r4.1.0.tar.gz https://github.com/mongodb/mongo-cxx-driver/releases/download/r4.1.0/mongo-cxx-driver-r4.1.0.tar.gz \
    && tar xzvf mongo-cxx-driver-r4.1.0.tar.gz \
    && cd /tmp/mongo-cxx-driver-r4.1.0/build/ \
    && cmake .. -DCMAKE_BUILD_TYPE=Release -DMONGOCXX_OVERRIDE_DEFAULT_INSTALL_PREFIX=OFF \
    && cmake --build . \
    && cmake --build . --target install \
    && ln -s /usr/local/include/bsoncxx/v_noabi/bsoncxx/* /usr/local/include/bsoncxx \
    && ln -s /usr/local/include/bsoncxx/v_noabi/bsoncxx/third_party/mnmlstc/core/ /usr/local/include/core \
    && ln -s /usr/local/include/mongocxx/v_noabi/mongocxx/* /usr/local/include/mongocxx/ \
    && ldconfig

RUN curl -L -o hiredis-cluster.tar.gz https://github.com/Nordix/hiredis-cluster/archive/refs/tags/0.12.0.tar.gz \
    && tar xzvf hiredis-cluster.tar.gz \
    && cd hiredis-cluster-0.12.0 \
    && mkdir build \
    && cd build \
    && cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_SSL=ON .. \
    && make \
    && make install \
    && echo "/usr/local/lib" > /etc/ld.so.conf.d/local.conf \
    && ldconfig

WORKDIR /app/das

COPY . .

ENTRYPOINT [ "make" ]
CMD [ "build-local" ]

