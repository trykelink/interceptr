# Dockerfile — Multi-stage production build for Interceptr
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

COPY requirements.txt ./requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --shell /usr/sbin/nologin interceptr

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app /app/app
COPY main.py /app/main.py
COPY policy.example.yaml /app/policy.example.yaml

RUN rm -rf /usr/local/lib/python3.12/ensurepip \
    /usr/local/lib/python3.12/idlelib \
    /usr/local/lib/python3.12/lib2to3 \
    /usr/local/lib/python3.12/tkinter \
    /usr/local/lib/python3.12/turtledemo \
    /usr/local/lib/python3.12/unittest \
    /usr/local/lib/python3.12/test \
    /usr/local/lib/python3.12/site-packages/pip* \
    /usr/local/lib/python3.12/site-packages/setuptools* \
    /usr/local/lib/python3.12/site-packages/wheel* \
    /usr/local/lib/python3.12/site-packages/pytest* \
    /usr/local/lib/python3.12/site-packages/iniconfig* \
    /usr/local/lib/python3.12/site-packages/pluggy* \
    /usr/local/lib/python3.12/site-packages/packaging* \
    /usr/local/bin/pip* \
    /root/.cache \
    && find /usr/local -type d -name "__pycache__" -prune -exec rm -rf {} + \
    && chown -R interceptr:interceptr /app

USER interceptr

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=10)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
