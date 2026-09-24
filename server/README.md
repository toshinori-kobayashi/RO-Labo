# rAthena Pre-Renewal 検証サーバ（server）

全体の入口は [../README.md](../README.md) です。

rAthena（GPL-3.0）を使った Ragnarok Online **Pre-Renewal** モードの検証用サーバです。AWS Sandbox アカウント上に Terraform で構築し、日本語 Windows クライアントから接続できるよう NPC・Mob 名・サーバメッセージの一部を日本語化しています。GitHub の RO-Labo リポジトリの `server/` として管理しています。Terraform state・`app/.env`・`backups/` は `.gitignore` で除外され、運用者の Mac にのみ存在します。

| 項目 | 値 |
|---|---|
| 最終更新 | 2026-09-24 |
| rAthena commit | `e985006171d2eb320ee512a653f4c83aea3d81b6`（master、2026-08-21） |
| PACKETVER | `20211103`（kRO 2021-11-03 RagexeRE 系） |
| Public IP（EIP） | `54.65.172.5` |

設定値・数値まで具体的な現行仕様は `docs/SPEC.md` を参照してください。

## 構成図

Internet → EIP → EC2（Docker Compose: mariadb → login-server:6900 → char-server:6121 → map-server:5121）。配布は Terraform → S3 → SSM Association、管理は SSM Session Manager / Run Command のみ（SSH 不可）。AWS リソース名を含む詳細な構成図は `docs/DESIGN.md` §3 を参照してください。

## ディレクトリ構成

```
server/
├── terraform/   インフラ定義（Terraform）
├── app/         EC2 の /srv/ro-server/app と 1:1（Docker Compose、rAthena、運用スクリプト）
├── scripts/     ローカル Mac 用運用スクリプト（SSM 経由のみ）
├── tools/       日本語化・検証用の補助ツール（Python）
├── docs/        仕様・運用・ツール・変更履歴・日本語化関連文書
└── backups/     翻訳スナップショット等（`tools/jp-backup.sh` の出力先）
```

## 前提ツール

以下のコマンドはすべて `server/` ディレクトリで実行する前提です（`terraform -chdir=terraform ...`、`scripts/...` の相対パスはそのまま使えます）。

| ツール | 用途 | 備考 |
|---|---|---|
| `aws` CLI + AWS SSO | AWS 操作全般 | プロファイル `sandbox-power` を使用。`aws sso login --profile sandbox-power` |
| `terraform` | インフラ構築・更新・撤去 | `>= 1.9`（`terraform/versions.tf`） |
| `session-manager-plugin` | SSM Session Manager でシェルに入る | `brew install --cask session-manager-plugin` |
| `nc` | ポート到達性確認（`scripts/verify.sh`） | macOS 標準搭載 |
| `python3` | SSM コマンドパラメータの JSON 生成（`scripts/lib/common.sh`） | macOS 標準搭載 |
| `docker` + `colima`（任意） | ローカルでの日本語化・DB 文字コードの事前検証 | `app/docker-compose.local.yml` を使用。AWS 環境の構築には不要 |

EC2 へは **SSH を使わず SSM 経由のみ**でアクセスします（22 番ポートは公開していません）。

## 構築手順

```sh
aws sso login --profile sandbox-power

terraform -chdir=terraform init
terraform -chdir=terraform plan
terraform -chdir=terraform apply
```

`apply` 1 回で「インフラ作成 → `app/` の S3 配布 → SSM Association 経由のビルド → 起動」まで完結します。内部の待ち上限は user-data 最大 10 分・SSM Association 最大 20 分・`apply` 自体は最大 50 分です（実測は 2026-09-23 初回構築で約 12 分）。50 分でタイムアウトしても配布処理がバックグラウンドで継続していることがあるため、以下で進捗を確認してから再度 `apply` してください（`apply` は冪等です）。

```sh
$(terraform -chdir=terraform output -raw ssm_association_status_command)
$(terraform -chdir=terraform output -raw ssm_deploy_log_command)
```

詳細は `docs/OPERATIONS.md`「インフラ変更」を参照してください。

## アプリ更新（`app/` 配下の変更）

`app/`（`docker-compose.yml`、`config.env`、`rathena/conf/import/*`、`rathena/overlay-utf8/*` 等）を編集し、`terraform -chdir=terraform plan` で確認してから `apply` します。判定基準は「`aws_s3_object.app` の `add` 以外に `destroy`/`replace` が出ないこと」です（特に `aws_instance.app` / `aws_ebs_volume.data` の replace は data EBS 上の DB・バックアップを失うため要注意）。反映確認は `scripts/verify.sh` に加え、`status.sh` の「map-server NPC パース」欄が 0 行であることを見てください（`delnpc:` の対象パスが存在しない場合は `npc_parsesrcfile: File not found` が出ますが、サーバは起動を継続します）。手順の詳細は `docs/OPERATIONS.md`「アプリ更新の標準手順」を参照してください。

## 運用・設定変更・トラブル対応

| やりたいこと | 参照 |
|---|---|
| 疎通確認 | `scripts/verify.sh`（詳細は `docs/TOOLS.md`）、期待値は `docs/SPEC.md` §3 |
| アカウント作成・パスワード・生年月日 | `docs/OPERATIONS.md`「アカウント運用」、既存一覧は `docs/SPEC.md` §7.4 |
| 起動・停止・再起動 | `docs/OPERATIONS.md`「再起動」「障害時」、`docs/TOOLS.md`「`scripts/ssm-shell.sh`」「`scripts/status.sh`」 |
| ログ確認 | `docs/OPERATIONS.md`「ログ調査」 |
| 倍率・PACKETVER・日本語 NPC の変更 | `docs/OPERATIONS.md`「倍率変更」「日本語化の運用手順」 |
| バックアップとリストア | `docs/OPERATIONS.md`「バックアップ・リストア詳細」 |
| セキュリティ要件 | `docs/DESIGN.md` §6、公開ポートは `docs/SPEC.md` §3 |
| 日本語化の現状（対象・数値・制約） | `docs/SPEC.md` §8 |
| 技術情報（rAthena 設定・conf 一覧） | `docs/SPEC.md` §2、§6 |
| Sandbox 固有の注意（aws-nuke、コスト目安） | `docs/OPERATIONS.md`「aws-nuke との付き合い方」、`docs/DESIGN.md` §3.3 |
| 撤去 | `docs/OPERATIONS.md`「撤去手順」 |
| トラブルシューティング | `docs/OPERATIONS.md`「トラブルシューティング集」 |

## 文書一覧

| 文書 | 内容 |
|---|---|
| `docs/SPEC.md` | 2026-09-24 時点の現行仕様（設定値・数値まで具体的に記載） |
| `docs/DESIGN.md`（v0.5） | 設計の背景・調査結果・決定理由 |
| `docs/OPERATIONS.md` | 日常運用の runbook |
| `docs/TOOLS.md` | ツール一覧 |
| `docs/CHANGELOG.md` | 変更履歴 |
| [../notes/archive/CLIENT_HANDOFF.md](../notes/archive/CLIENT_HANDOFF.md) | HISTORICAL（旧ネイティブクライアント向け。現行の接続仕様は SPEC §6〜§7、実クライアントは RO-Labo [../client/README.md](../client/README.md)） |
| `docs/JP_GLOSSARY.md` | 日本語化の用語集 |
| `docs/JP_TRANSLATION_RULES.md` | 日本語化の翻訳ルール |
| `docs/JP_NPC_PLAN.md` | NPC 日本語化の拡張計画と進捗 |
| `docs/JP_COVERAGE_PHASE2.md` | 日本語化 第 2 フェーズの棚卸し |

## 注意

Sandbox の aws-nuke（毎日 05:00 JST）、秘密情報の扱い、`terraform destroy` の影響は `docs/OPERATIONS.md` を参照してください。
