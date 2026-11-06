# serena

[Serena](https://github.com/oraios/serena) を、言語サーバーによるコードの解析（シンボルの検索・参照の追跡など）を提供する MCP サーバーとしてホストします。

仕様は [SPEC.md](SPEC.md) を参照してください。

## 接続 URL

```text
http://localhost:9104/serena/mcp
```

ポートは `MCP_GATEWAY_PORT`（既定 `9104`）で変更できます。

## クライアント設定例

Claude Code:

```bash
claude mcp add --transport http serena http://localhost:9104/serena/mcp
```

`.mcp.json` などの設定ファイル:

```json
{
  "mcpServers": {
    "serena": {
      "type": "http",
      "url": "http://localhost:9104/serena/mcp"
    }
  }
}
```

## 起動

```bash
make up
```

起動前に、`/workspace` の各プロジェクトの依存関係をボリュームに入れます（Compose の `pre_start`）。プロジェクトの依存関係を変更したときは、コンテナを作り直します。

```bash
docker compose up -d --wait --force-recreate mcp-serena
```

## 制約

- プロジェクトは読み取り専用でマウントするため、serena の編集系のツールは使えません
- 対応する言語は Python / C# / Go / TypeScript です（[SPEC.md の言語サーバー](SPEC.md#言語サーバー) 参照）
- web ダッシュボードは使えません
- Docker Compose v5.3.0 以上が必要です（`pre_start` を使うため）
- プロジェクト内に重ねるボリュームのマウント先は、ホスト側に root 所有の空のディレクトリとして作られます（rootful の Docker の場合）
- 他のプロジェクトで使うときは、`compose.yaml` のマウント元と、プロジェクト内に重ねるボリュームのパスを、そのプロジェクトの構成に合わせて変更します
