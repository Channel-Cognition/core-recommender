FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/python3 -m pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt && \
    /opt/venv/bin/pip install chancog-0.3.dev132-py3-none-any.whl && \
    chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]