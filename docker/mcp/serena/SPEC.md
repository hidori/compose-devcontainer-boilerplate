# serena

[Serena](https://github.com/oraios/serena) を、[SPEC.md](../../../SPEC.md) に基づいてホストするための仕様。

## 基本情報

| 項目 | 値 |
| --- | --- |
| 識別子 | `serena` |
| サービス名 | `mcp-serena` |
| ネットワーク | `mcp-serena`（internal）。`pre_start` の依存関係の取得のみ `default` にも所属する |
| 公開パス | `/serena/mcp` |
| 上流 | `http://mcp-serena:8000/mcp`（Streamable HTTP） |

- web ダッシュボードは無効とし、公開しない

## マウント

- プロジェクトのルートを `/workspace` にボリュームマウントで渡す
  - マウントは読み取り専用（`:ro`）とする（[SPEC.md のセキュリティ](../../../SPEC.md#セキュリティ) 参照）
  - `/workspace` を 1 つの serena プロジェクトとして解析する
- serena のプロジェクト設定（`project.yml`）は `read_only: true` とし、編集系のツールを無効にする

## 言語サーバー

| 言語 | serena の言語サーバー |
| --- | --- |
| Python | `python_basedpyright` |
| C# | `csharp`（Roslyn） |
| Go | `go`（gopls） |
| TypeScript | `typescript`（typescript-language-server） |

- 言語サーバーと実行環境（Python / Node.js / Go / .NET）はイメージに入れ、実行時に取得させない（`mcp-serena` は外部と通信できないため）
  - 公式イメージ（`ghcr.io/oraios/serena`）には .NET と Go がなく、言語サーバーも実行時に取得するため、完結できない。そのためカスタムの Dockerfile を使う
  - 実行環境は公式イメージを digest で固定して取り込む
  - basedpyright は `uv.lock`、gopls は `go/go.mod` と `go/go.sum`、TypeScript の言語サーバーは `ts/package-lock.json` で固定する
  - Roslyn は serena に組み込みの版を、ビルド時に serena が sha256 を検証して展開する
- 言語サーバーは `$SERENA_HOME/language_servers/static/` に置く（serena が管理するディレクトリ）
  - `$SERENA_HOME` はボリュームにしない（イメージの更新を反映させるため）

## ボリューム

- 書き込みが必要な場所は、名前付きボリュームに置く
- プロジェクト内（読み取り専用の `/workspace` の上に重ねる）
  - 依存関係とビルド出力（例: `.venv`、`node_modules`、`obj`、`bin`）
  - 重ねる場所はプロジェクトの構成に合わせて `compose.yaml` に定義する
  - ホストで作ったものは使わない（ホストとコンテナでプラットフォームが異なると動かない場合があるため）
- プロジェクト外
  - serena のプロジェクトのデータ（`.serena` フォルダ）: `$SERENA_HOME/projects`
  - serena のグローバルなメモリー: `$SERENA_HOME/memories`
  - キャッシュ: `~/.cache`、`~/go`、`~/.nuget`、`~/.dotnet`

## 依存関係のインストール

- `mcp-serena` の `pre_start`（Compose の init コンテナ）で、起動前に次の順で実行する
  1. プロジェクト内に重ねるボリュームの、ホスト側のマウント先を作る
     - `/workspace` を書き込み可能でマウントし直すことで、Docker がマウント先を作る（コマンドは何もしない）
     - マウント先のパスはボリュームの定義から決まるため、別に管理しない
     - rootful の Docker では、マウント先は root 所有の空のディレクトリになる
  2. `/workspace` の各プロジェクトの依存関係を、プロジェクト内のボリュームに入れる（`deps.sh`）
     - `/workspace` は読み取り専用のまま実行する
     - 依存関係の取得のため、このステップだけ `default` にも所属させる
     - serena のプロセスの中で依存関係のインストールを実行しないため、init コンテナで行う
- `pre_start` は一度成功すると、コンテナを作り直すまで再実行されない
- プロジェクトの種類は、サブフォルダにあるファイルで判定する

| ファイル | 実行するコマンド |
| --- | --- |
| `uv.lock` | `uv sync --frozen --no-install-project` |
| `package-lock.json` | `npm ci --ignore-scripts` |
| `*.csproj` | `dotnet restore` |
| `go.mod` | `go mod download` |

- `npm ci` は `--ignore-scripts` でインストールスクリプトを実行しない
- `dotnet restore` は MSBuild を経由するため、プロジェクトのビルド定義が実行される可能性がある
