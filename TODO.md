# TODO

## 機能

- [ ] db コンテナを追加する
  - MySQL と PostgreSQL
  - サービス名（案: `db-mysql`、`db-postgres`）
  - ネットワーク（外部から到達させず、dev コンテナからのみ接続させる）
  - ホストへのポート公開の有無（公開する場合は `127.0.0.1` に bind し、環境変数で変更可能にする）
  - 接続情報（ユーザー、パスワードなど）の置き場所
  - 公式イメージの脆弱性検査の扱い（SPEC.md の「方針」に追加する）
- [ ] dev コンテナを追加する
  - ベースイメージ（`ubuntu` または `mcr.microsoft.com/devcontainers/base:ubuntu`）
  - コンテナに入れるもの（言語ランタイム、mise など）
  - `.devcontainer/devcontainer.json`
  - サービス名（案: `devcontainer`）
  - dev コンテナから MCP gateway を使うか（使う場合は、gateway で許可する `Host` を追加する）
  - 公式イメージの脆弱性検査の扱い（外部と通信するため、MCP サーバーの「ネットワーク分離で守る」は当てはまらない）

## 開発ツール

- [ ] 開発ツールの外部依存を軽量化する
  - 対象は、Node.js や Python のような大型で影響の大きい外部依存（ツール自体が脆弱性を持ちうるため）
  - 開発ツールの実行場所（ホスト / dev コンテナ / 使い捨てコンテナ）を決める
  - Docker を使う作業（`make up` / `down` / `test`、`make scan-mcp-nginx`）はホストに残す
    - dev コンテナから Docker を操作するには、Docker ソケットのマウントか Docker-in-Docker が必要で、セキュリティの方針と合わないため
  - Python を受け入れるか決める（多くのディストリビューションに標準で入っているため、受け入れる案がある）
    - 受け入れる場合: mise の `python` を外し、ディストリビューション標準の `python3` を使うか
      - `scripts/osv-scan.py` と `scripts/osv-format.py` は Python 3.10 以上が必要（`list[str] | None` などの型注釈）
      - `yamllint`（現在は mise の Python で venv を作成）が標準の Python で動くか確認する
    - 外す場合: `scripts/osv-scan.py` と `scripts/osv-format.py` の置き換え（`jq` での集計など）と、`yamllint` の置き換え（候補は未調査）
  - `uv.lock` の作成と監査（`uv audit` など）はコンテナで実行する
  - Node.js（`package-lock.json` 作成時の `npm audit` など）はホストに入れず、コンテナで実行する

## MCP サーバー

- [ ] serena の依存関係のインストール（`pre_start` と `deps.sh`）を見直す
  - 重ねるボリュームがないまま `/workspace` 直下のサブディレクトリにロックファイルを置くと、読み取り専用の場所に書き込もうとして起動に失敗する（推定、未検証）
  - dev コンテナがプロジェクト内に入れた依存関係を、serena がそのまま読めるか確認する
- [ ] `.env` が MCP サーバーから見える（`/workspace/.env`）問題に対処する
  - 秘密情報を置く場所の設計と合わせて決める

## 文書

- [ ] README.md と SPEC.md の見出し（`docker-mcp-servers`）と主旨を、dev コンテナを使う開発環境のボイラープレートに書き換える
- [ ] AGENTS.md の「対象 MCP サーバーの SPEC.md」という前提を、db / dev コンテナの作業にも当てはまる形にする
- [ ] README.md のディレクトリ構成に、`.github/` と `TODO.md` を追加する
- [ ] 開発ツールの脆弱性検査（`make scan-tools`。Critical のみ失敗）の基準と理由を SPEC.md に記載する
- [ ] 公式イメージの digest を更新する手順とタイミングを決める
- [ ] コミットメッセージにしか残っていない判断の理由を洗い出し、SPEC.md などに移す
  - 初回リリース前に履歴を 1 コミットにまとめるため、コミットメッセージの理由は消える

## 後片付け

- [ ] リモートのブランチ `claude/project-thread-5ygs5m` を削除する（PR #1 はマージ済み）
- [ ] 使われなくなった Docker ボリュームを削除する（ローカル環境）
  - `compose-devcontainer-boilerplate_mcp-serena-{py-venv,ts-node-modules,cs-obj,cs-bin}`
