FROM python:3.8-buster

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /rele
LABEL python_version=python

COPY Makefile ./
COPY requirements requirements/

RUN make install-dev-requirements

COPY . .

CMD ["make", "clean", "lint", "test"]
