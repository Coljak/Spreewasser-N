FROM ubuntu:jammy
LABEL maintainer="Colja"

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

ARG DEV=false
RUN apt-get update -qq && apt-get install -y -qq \
    # std libs
    git less nano curl \
    ca-certificates \
    wget build-essential\
    # python basic libs
    python3.10 python3.10-dev python3.10-venv gettext \
    # geodjango
    gdal-bin binutils libproj-dev libgdal-dev \
    # postgresql
    libpq-dev postgresql-client && \
    apt-get clean all && rm -rf /var/apt/lists/* && rm -rf /var/cache/apt/* && \
    # install pip
    wget https://bootstrap.pypa.io/get-pip.py && python3.10 get-pip.py && rm get-pip.py && \
    pip3 install --no-cache-dir setuptools wheel -U && \
    python3 -m venv /py && \
    #/py/bin/pip3 install --upgrade pip3 && \
    #apk add --update --no-cache postgresql-client && \
    # apk add --update --no-cache --virtual .tmp-build-deps \
    #     build-base postgresql-dev musl-dev && \
    /py/bin/pip3 install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip3 install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    #apk del .tmp-build-deps 
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"



