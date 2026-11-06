# repomix

[Repomix](https://github.com/yamadashy/repomix) を、[SPEC.md](../../../SPEC.md) に基づいてホストするための仕様。

## 基本情報

| 項目 | 値 |
| --- | --- |
| 識別子 | `repomix` |
| サービス名 | `mcp-repomix` |
| ネットワーク | `mcp-repomix`（internal） |
| 公開パス | `/repomix/mcp` |
| 上流 | `http://mcp-repomix:8000/mcp`（Streamable HTTP） |

## イメージ

- repomix の MCP サーバーは stdio のみに対応するため、[mcp-proxy](https://github.com/sparfenyuk/mcp-proxy) で Streamable HTTP に変換する
  - 公式イメージ（`ghcr.io/yamadashy/repomix`）は HTTP で公開できず、完結できないため、カスタムの Dockerfile を使う
- repomix は `package-lock.json`、mcp-proxy は `uv.lock` で固定する
- 実行環境（Python / Node.js）は公式イメージを digest で固定して取り込む

## 起動

- `repomix --mcp --sandbox /workspace` で起動する
  - ファイルを扱うツールを `/workspace` の中に限定する
  - リモートのリポジトリの取り込み、スキルの生成、外部の出力の添付を無効にする（外部と通信できないため）
- パックした出力は、コンテナ内の一時ディレクトリに書き込まれる（`/workspace` には書き込まない）

## マウント

- `example/` を `/workspace` にボリュームマウントで渡す
  - マウントは読み取り専用（`:ro`）とする
