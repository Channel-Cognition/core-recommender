FROM python:3.9.7-slim

COPY . /app
WORKDIR /app

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/python3 -m pip install --upgrade pip && \
    /opt/venv/bin/pip install --default-timeout=100 future -r requirements.txt && \
    chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]