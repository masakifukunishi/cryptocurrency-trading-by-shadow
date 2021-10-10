FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
  sudo \
  wget \
  vim \
  make \
  gcc

WORKDIR /opt
# anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh && \
  sh Anaconda3-2021.05-Linux-x86_64.sh -b -p /opt/anaconda3 && \
  rm -f Anaconda3-2021.05-Linux-x86_64.sh

ENV PATH /opt/anaconda3/bin:$PATH

RUN pip install \
  websocket-client

WORKDIR /src