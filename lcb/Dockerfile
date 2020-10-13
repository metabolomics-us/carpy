FROM python:3.8-slim

RUN apt update && apt upgrade -y
RUN apt install -y bash git docker

# setup python env
ENV PYTHONUNBUFFERED=1

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools wheel

# setup LCB
RUN mkdir /lcb
WORKDIR /lcb
COPY requirements.txt /lcb
COPY . /lcb

# update all dependencies
RUN pip install -r requirements.txt
RUN pip install -e .
