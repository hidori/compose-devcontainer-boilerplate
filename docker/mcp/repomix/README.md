# repomix

[Repomix](https://github.com/yamadashy/repomix) を、コードベースを AI 向けに 1 つのファイルへまとめる（パックする）MCP サーバーとしてホストします。

仕様は [SPEC.md](SPEC.md) を参照してください。

## 接続 URL

```text
http://localhost:9104/repomix/mcp
```

ポートは `MCP_GATEWAY_PORT`（既定 `9104`）で変更できます。

## クライアント設定例

Claude Code:

```bash
claude mcp add --transport http repomix http://localhost:9104/repomix/mcp
```

`.mcp.json` などの設定ファイル:

```json
{
  "mcpServers": {
    "repomix": {
      "type": "http",
      "url": "http://localhost:9104/repomix/mcp"
    }
  }
}
```

## 制約

- 扱えるのは `/workspace`（`example/`）の中だけです。パスは `/workspace` からの相対パスで指定します
- リモートのリポジトリの取り込み（`pack_remote_repository`）は使えません
- 他のプロジェクトで使うときは、`compose.yaml` のマウント元を、そのプロジェクトに合わせて変更します
