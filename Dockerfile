# syntax=docker/dockerfile:1
#
# One Dockerfile, two build targets (best practice):
#   CPU (default):  docker build -t profanity-filter:cpu --target cpu .
#   GPU:            docker build -t profanity-filter:gpu --target gpu .
#
# GPU runs need NVIDIA Container Toolkit:
#   docker run --gpus all ...

ARG PYTHON_VERSION=3.11

############################
# Shared app payload
############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS app-src
WORKDIR /src
COPY requirements.txt ./
COPY *.py ./
COPY profanity_words.csv ./
COPY profanity_words_optional_soft.csv ./


############################
# CPU image (default)
############################
FROM python:${PYTHON_VERSION}-slim-bookworm AS cpu

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PROFANITY_FILTER_DEVICE=cpu \
    HF_HOME=/cache/huggingface \
    XDG_CACHE_HOME=/cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=app-src /src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt "gradio>=4.0.0"

COPY --from=app-src /src/ ./

RUN mkdir -p /data /cache \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /data /cache

USER appuser
WORKDIR /data
VOLUME ["/data", "/cache"]
EXPOSE 7860

# Default: CLI help. Override command for clean.py / app.py.
ENTRYPOINT ["python3"]
CMD ["/app/clean.py", "--help"]


############################
# GPU image (CUDA runtime)
############################
FROM nvidia/cuda:12.3.2-runtime-ubuntu22.04 AS gpu

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    HF_HOME=/cache/huggingface \
    XDG_CACHE_HOME=/cache
# Leave PROFANITY_FILTER_DEVICE unset so the app auto-selects CUDA when available.

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        ffmpeg \
        ca-certificates \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=app-src /src/requirements.txt ./
# faster-whisper / CTranslate2 use host CUDA libs from the NVIDIA base image.
RUN pip3 install --no-cache-dir -r requirements.txt "gradio>=4.0.0"

COPY --from=app-src /src/ ./

RUN mkdir -p /data /cache \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app /data /cache

USER appuser
WORKDIR /data
VOLUME ["/data", "/cache"]
EXPOSE 7860

ENTRYPOINT ["python3"]
CMD ["/app/clean.py", "--help"]


# Default target when users run: docker build .
FROM cpu AS default
