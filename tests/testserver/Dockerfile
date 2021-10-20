FROM python:3.8-alpine
RUN apk update && apk upgrade
RUN apk add git gcc dev86 musl-dev make

RUN git clone https://github.com/micropython/micropython.git
WORKDIR /micropython/ports/unix

RUN make submodules
RUN apk add bsd-compat-headers
RUN make install
RUN git submodule update --init --recursive