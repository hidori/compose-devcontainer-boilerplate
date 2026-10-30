# example

docker-mcp-servers の MCP サーバーを利用する側の、仮想のプロジェクトです。

Serena などの MCP サーバーから参照・解析される題材として、複数のファイルにまたがるシンボルを持つ小さなコード（カートと商品）を言語ごとに置いています。

| ディレクトリ | 言語 | 依存関係の定義 |
| --- | --- | --- |
| `py/` | Python | `pyproject.toml`、`uv.lock` |
| `cs/` | C# | `SampleApp.csproj` |
| `go/` | Go | `go.mod` |
| `ts/` | TypeScript | `package.json`、`package-lock.json` |
