# パイプの途中のコマンドの失敗を、パイプ全体の終了コードに反映させる（osv-scan.py | osv-format.py など）
SHELL := bash
.SHELLFLAGS := -o pipefail -c

MISE := mise exec --

# git 管理下（未追跡を含む、.gitignore 対象を除く）のファイル
FILES := $(shell git ls-files --cached --others --exclude-standard)

MARKDOWN_FILES := $(filter %.md,$(FILES))
YAML_FILES := $(filter %.yml %.yaml,$(FILES))
SHELL_FILES := $(filter %.sh,$(FILES))
DOCKERFILES := $(filter Dockerfile %/Dockerfile %.Dockerfile,$(FILES))
TOML_FILES := $(filter %.toml,$(FILES))
WORKFLOW_FILES := $(filter .github/workflows/%.yml .github/workflows/%.yaml,$(FILES))

.DEFAULT_GOAL := help

.PHONY: help prepare-env up down test install-tools scan-tools scan-mcp-nginx lint lint-markdown lint-yaml lint-shell lint-dockerfile lint-actions lint-toml lint-secrets

help: ## ターゲットの一覧を表示する
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

prepare-env: ## .env がなければ .env.example から作成する
	[ -f .env ] || cp .env.example .env

up: prepare-env ## サービスをビルドして起動し、healthy になるまで待つ
	docker compose up -d --build --wait

down: prepare-env ## サービスを停止・削除する
	docker compose down

test: ## gateway のヘルスチェックを行う
	curl -fsS http://$$(docker compose port mcp-gateway 8080)/gateway/healthz

install-tools: ## 開発ツールをインストールし、脆弱性を検査する
	mise install $$(mise ls --local | awk '{print $$1}')
	$(MAKE) scan-tools

# Critical（CVSS 9.0 以上）があれば失敗する。全ツールをスキャンしてから合否を出す
# High（CVSS 7.0 以上）は明細を表示するが、失敗にはしない。Medium 以下は件数のみ（明細は量が多いため）
# osv-scanner の終了コードは 0（脆弱性なし）と 1（脆弱性あり）のみ正常とする
scan-tools: ## 開発ツールの脆弱性を検査する
	( status=0; \
	json=$$(mktemp); \
	trap 'rm -f "$$json"' EXIT; \
	trap 'exit 1' HUP INT TERM PIPE; \
	for tool in $$(mise ls --local | awk '{print $$1}'); do \
		rc=0; \
		$(MISE) osv-scanner scan source --x-plugins artifact --no-ignore --allow-no-lockfiles \
			--verbosity error --format json --all-packages -r "$$(mise where $$tool)" > "$$json" || rc=$$?; \
		if [ $$rc -ne 0 ] && [ $$rc -ne 1 ]; then \
			echo "ERROR: $$tool: osv-scanner exited with $$rc" >&2; \
			status=1; \
			continue; \
		fi; \
		$(MISE) python3 -I scripts/osv-scan.py "$$tool" < "$$json" || status=1; \
	done; \
	exit $$status ) | $(MISE) python3 -I scripts/osv-format.py

# High 以上（CVSS 7.0 以上）または深刻度不明で、修正版があるものがあれば失敗する（修正版がないものは警告）
# osv-scanner の終了コードは 0（脆弱性なし）と 1（脆弱性あり）のみ正常とする
scan-mcp-nginx: prepare-env ## gateway（nginx）のコンテナイメージをビルドし、脆弱性を検査する
	docker compose build mcp-gateway
	image="$$(docker compose config --images mcp-gateway):latest"; \
	json=$$(mktemp); \
	trap 'rm -f "$$json"' EXIT; \
	trap 'exit 1' HUP INT TERM PIPE; \
	rc=0; \
	$(MISE) osv-scanner scan image --verbosity error --format json --all-packages "$$image" > "$$json" || rc=$$?; \
	if [ $$rc -ne 0 ] && [ $$rc -ne 1 ]; then \
		echo "ERROR: $$image: osv-scanner exited with $$rc" >&2; \
		exit 1; \
	fi; \
	$(MISE) python3 -I scripts/osv-scan.py --policy fixable-high "$$image" < "$$json" | $(MISE) python3 -I scripts/osv-format.py

lint: lint-markdown lint-yaml lint-shell lint-dockerfile lint-actions lint-toml lint-secrets ## すべての lint を実行する

lint-markdown: ## Markdown を lint する
ifneq ($(MARKDOWN_FILES),)
	$(MISE) rumdl check $(MARKDOWN_FILES)
endif

lint-yaml: ## YAML を lint する
ifneq ($(YAML_FILES),)
	$(MISE) yamllint --strict $(YAML_FILES)
endif

lint-shell: ## シェルスクリプトを lint する
ifneq ($(SHELL_FILES),)
	$(MISE) shellcheck $(SHELL_FILES)
endif

lint-dockerfile: ## Dockerfile を lint する
ifneq ($(DOCKERFILES),)
	$(MISE) hadolint $(DOCKERFILES)
endif

lint-actions: ## GitHub Actions のワークフローを lint する
ifneq ($(WORKFLOW_FILES),)
	$(MISE) jactionlint $(WORKFLOW_FILES)
endif

lint-toml: ## TOML を lint する
ifneq ($(TOML_FILES),)
	$(MISE) tombi lint --error-on-warnings $(TOML_FILES)
endif

lint-secrets: ## シークレットの混入を検査する
	$(MISE) betterleaks git --no-banner .
	$(MISE) betterleaks dir --no-banner .
