FROM ghcr.io/astral-sh/uv:python3.14-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR /rele
LABEL python_version=python

COPY . .

RUN uv sync --locked --all-groups --all-extras

CMD ["make", "clean", "lint", "test"]
