# FROM tiangolo/uwsgi-nginx-flask:flask-python3.5
FROM python:3.6-stretch

MAINTAINER luckydonald

ARG FOLDER
# Sane defaults for pip
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on

# To force docker to build the RUN step again, change this value.
ARG DOCKER_CACHE_KILLER=2

RUN set -x \
    # make überstart executable
	&& apt-get update \
	&& apt-get install -y --no-install-recommends \
    # Install nginx, and stuff
        ca-certificates \
        gettext-base \
    # utilities
        nano \
    # install python wsgi
    && rm -rfv /var/lib/apt/lists/*

WORKDIR /app
CMD ["python", "main.py"]
HEALTHCHECK --start-period=5s CMD ["python", "healthcheck.py"]

COPY $FOLDER/requirements.txt   /config/
RUN pip install -r /config/requirements.txt

COPY $FOLDER/code /app
