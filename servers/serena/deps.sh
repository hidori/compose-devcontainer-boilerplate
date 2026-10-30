#!/bin/sh
# /workspace 直下の各プロジェクトの依存関係を、プロジェクト内に重ねたボリュームへ入れる
# root で起動し、ボリュームの所有者を serena に変えてから serena の権限で実行する
set -eu

if [ "$(id -u)" -eq 0 ]; then
    for dir in /workspace/*/.venv /workspace/*/node_modules /workspace/*/obj /workspace/*/bin; do
        if [ -d "$dir" ]; then
            chown serena:serena "$dir"
        fi
    done
    exec setpriv --reuid=serena --regid=serena --init-groups --inh-caps=-all "$0" "$@"
fi

for project in /workspace/*/; do
    cd "$project"
    if [ -f uv.lock ]; then
        echo "uv sync: $project"
        uv sync --frozen --no-install-project
    fi
    if [ -f package-lock.json ]; then
        echo "npm ci: $project"
        npm ci --ignore-scripts --no-audit --no-fund
    fi
    for csproj in *.csproj; do
        [ -f "$csproj" ] || continue
        echo "dotnet restore: $project$csproj"
        dotnet restore "$csproj"
    done
    if [ -f go.mod ]; then
        echo "go mod download: $project"
        go mod download
    fi
done
