FROM python:3.8-buster

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /rele
LABEL python_version=python

COPY . .

RUN make install-dev-requirements

CMD ["make", "clean", "lint", "test"]
