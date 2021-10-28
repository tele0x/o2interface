FROM python:3.10-slim-buster

RUN apt-get update; apt-get install -y git gcc
COPY requirements.txt /tmp/
COPY constraints.txt /tmp/

RUN pip install -r /tmp/requirements.txt -c /tmp/constraints.txt

COPY requirements-test.txt /tmp/
RUN pip install -r /tmp/requirements-test.txt

RUN mkdir -p /src
COPY o2ims/ /src/o2ims/
COPY o2dms/ /src/o2dms/
COPY o2common/ /src/o2common/
COPY setup.py /src/

RUN pip install -e /src

COPY tests/ /tests/

WORKDIR /src