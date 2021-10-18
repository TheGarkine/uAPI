FROM python:3.8-alpine

RUN apk update && apk upgrade
RUN apk add git gcc dev86 musl-dev make

RUN git clone https://github.com/micropython/micropython.git
WORKDIR /micropython/mpy-cross
RUN make
ENV PATH=$PATH:/micropython/mpy-cross

WORKDIR /
ADD create_single_file.py /create_single_file.py
CMD python create_single_file.py && mpy-cross /build/uAPI.py