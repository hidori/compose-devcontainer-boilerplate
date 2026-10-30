# 実行環境は公式イメージから digest で固定して取り込む
FROM ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff AS uv

# repomix 本体は package-lock.json で固定して入れる
FROM node:24.22.2-trixie-slim@sha256:54f84b4cf8432b21aaffd5d3ce8d41e12cea0d10d33c09d2f3c9879d49d6b446 AS repomix
WORKDIR /opt/repomix
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --omit=dev --no-audit --no-fund \
    && npm cache clean --force

FROM python:3.14.9-slim-trixie@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH=/opt/repomix/.venv/bin:/opt/repomix/node_modules/.bin:$PATH

COPY --from=uv /uv /usr/local/bin/
COPY --from=repomix /usr/local/bin/node /usr/local/bin/node
COPY --from=repomix /opt/repomix/node_modules /opt/repomix/node_modules

RUN groupadd --gid 10001 repomix \
    && useradd --uid 10001 --gid repomix --home-dir /home/repomix --create-home --shell /usr/sbin/nologin repomix

# stdio の MCP サーバーを Streamable HTTP で公開する mcp-proxy は uv.lock で固定して入れる
WORKDIR /opt/repomix
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

USER 10001:10001
WORKDIR /home/repomix

# --sandbox: ファイル操作を /workspace に限定し、リモートのリポジトリの取り込みなどを無効にする
CMD ["mcp-proxy", "--host", "0.0.0.0", "--port", "8000", "--", "repomix", "--mcp", "--sandbox", "/workspace"]
