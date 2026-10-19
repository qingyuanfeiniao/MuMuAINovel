# 使用本机已构建的前端和 INT8 模型，避免小服务器编译前端或转换模型。
ARG PYTHON_IMAGE=python:3.13.7-slim-bookworm
FROM ${PYTHON_IMAGE}

USER root
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
ENV PATH=/opt/ai-novel-venv/bin:/usr/local/bin:/usr/bin:/bin \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY requirements.lock /tmp/ai-novel-requirements.lock
RUN /usr/local/bin/python -m venv /opt/ai-novel-venv \
    && /opt/ai-novel-venv/bin/python -m pip install --no-cache-dir --no-compile \
       --only-binary=:all: --index-url "${PIP_INDEX_URL}" -r /tmp/ai-novel-requirements.lock \
    && rm /tmp/ai-novel-requirements.lock

COPY low-memory-requirements.txt /tmp/ai-novel-low-memory-requirements.txt
RUN python -m pip install --no-cache-dir --no-compile --only-binary=:all: \
    --index-url "${PIP_INDEX_URL}" -r /tmp/ai-novel-low-memory-requirements.txt \
    && rm /tmp/ai-novel-low-memory-requirements.txt

COPY backend/ /app/
COPY embedding/ /app/embedding/
COPY LICENSE /app/LICENSE
RUN chmod +x /app/scripts/entrypoint.sh

USER 10001:10001
EXPOSE 8000
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
