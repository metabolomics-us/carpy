FROM docker:dind

RUN apk update
RUN apk upgrade
RUN apk add --no-cache --update bash git openssh build-base gcc abuild binutils binutils-doc gcc-doc cmake cmake-doc extra-cmake-modules extra-cmake-modules-doc jpeg jpeg-dev zlib zlib-dev python3 python3-dev  g++ python3-dev libffi-dev openssl-dev python3 postgresql-dev gcc python3-dev musl-dev openblas-dev lapack-dev gfortran libxml2-dev libxslt-dev

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
