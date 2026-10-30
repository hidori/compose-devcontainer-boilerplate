#!/bin/sh
# プロジェクト設定を、ボリューム上のプロジェクトの .serena フォルダへ配置してから起動する
set -eu

mkdir -p "$SERENA_HOME/projects/workspace"
cp /opt/serena/project.yml "$SERENA_HOME/projects/workspace/project.yml"

exec "$@"
