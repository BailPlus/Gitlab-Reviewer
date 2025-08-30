FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 安装 uv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s /root/.local/bin/uv /usr/local/bin/uv

# 依赖安装（使用 uv.lock）
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev | uv pip install --system -r -

# 拷贝源码并设定 Python 路径
COPY . .
ENV PYTHONPATH=/app

EXPOSE 8000
ENV PORT=8000

# 入口改为 app:app（指向 `back/app/__init__.py` 中的 app 实例）
CMD ["sh", "-c", "uvicorn ${UVICORN_APP:-app:app} --host 0.0.0.0 --port ${PORT:-8000}"]