# 実行環境は公式イメージから digest で固定して取り込む
FROM ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff AS uv
FROM node:24.22.2-trixie-slim@sha256:54f84b4cf8432b21aaffd5d3ce8d41e12cea0d10d33c09d2f3c9879d49d6b446 AS node
FROM mcr.microsoft.com/dotnet/sdk:10.0.403-noble@sha256:de4fe90a98845d75910b9769662465c84de1a934665c431279d1382b2bddc02b AS dotnet

# Go の言語サーバー（gopls）は go.mod / go.sum で固定してビルドする
FROM golang:1.27.3-trixie@sha256:c65ecfe613b539ac74c62a4c3b2c27e8f8a6076384c8f27e8a3c0f3be17cc385 AS gopls
WORKDIR /src
COPY go/go.mod go/go.sum ./
RUN GOTOOLCHAIN=local CGO_ENABLED=0 go build -mod=readonly -trimpath -o /out/gopls golang.org/x/tools/gopls

FROM python:3.14.9-slim-trixie@sha256:35caba83af2fe6da9a5d922f9b0156f21d1246a48278c58a08bd253303ba42e8

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GOTOOLCHAIN=local \
    GOTELEMETRY=off \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1 \
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    HOME=/home/serena \
    SERENA_HOME=/home/serena/.serena \
    PATH=/opt/serena/.venv/bin:/opt/serena/bin:/usr/local/go/bin:$PATH

COPY --from=uv /uv /uvx /usr/local/bin/
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
COPY --from=dotnet /usr/share/dotnet /usr/share/dotnet
COPY --from=gopls /usr/local/go /usr/local/go
COPY --from=gopls /out/gopls /opt/serena/bin/gopls

RUN ln -s ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -s ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && ln -s /usr/share/dotnet/dotnet /usr/local/bin/dotnet \
    && groupadd --gid 10001 serena \
    && useradd --uid 10001 --gid serena --home-dir /home/serena --create-home --shell /usr/sbin/nologin serena \
    && install -d -o serena -g serena \
        /home/serena/.serena \
        /home/serena/.serena/language_servers \
        /home/serena/.serena/language_servers/static \
        /home/serena/.serena/language_servers/static/TypeScriptLanguageServer \
        /home/serena/.serena/language_servers/static/TypeScriptLanguageServer/ts-lsp \
        /home/serena/.serena/projects /home/serena/.serena/memories \
        /home/serena/.cache /home/serena/go /home/serena/.nuget /home/serena/.dotnet

# serena 本体と Python の言語サーバー（basedpyright）
WORKDIR /opt/serena
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --no-cache

COPY project.yml ./
COPY --chmod=755 entrypoint.sh deps.sh ./bin/
COPY --chown=10001:10001 serena_config.yml /home/serena/.serena/serena_config.yml

# 作成したディレクトリは、ボリュームのマウント先を兼ねる（名前付きボリュームの初期所有者が serena になる）
USER 10001:10001

# 言語サーバーは $SERENA_HOME/language_servers/static/<クラス名>/ に置く（serena が管理するディレクトリ）
# $SERENA_HOME はボリュームにせず、イメージの更新が反映されるようにする

# TypeScript の言語サーバーは、package-lock.json で固定して入れる
# （serena 2.1.0 の既定版 typescript 5.9.3 / typescript-language-server 5.1.3 は "ts-lsp" に置かれる）
WORKDIR /home/serena/.serena/language_servers/static/TypeScriptLanguageServer/ts-lsp
COPY --chown=serena:serena ts/package.json ts/package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund \
    && npm cache clean --force

# C# の言語サーバー（Roslyn）は serena に組み込みの版を、serena が sha256 を検証して展開する
RUN serena download-ls-dependencies csharp

WORKDIR /home/serena
ENTRYPOINT ["/opt/serena/bin/entrypoint.sh"]
CMD ["serena", "start-mcp-server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000", "--project", "/workspace", "--enable-web-dashboard", "false"]
