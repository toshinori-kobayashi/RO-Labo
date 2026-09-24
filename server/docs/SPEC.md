# 現行仕様書

最終更新: 2026-09-24

> **注: 2026-09-24 に AWS 環境は撤去済み。** 本書は撤去直前の最終状態の記録です。再構築すると EIP・インスタンス ID・Security Group ID・SSM Association ID 等の識別子は変わります。

このドキュメントは 2026-09-24 時点の rAthena Pre-Renewal 検証サーバの**現状**を、設定値・名前・数値まで具体的に記録したものです。「あるべき姿」や将来計画ではなく、実機・リポジトリで確認できる状態のみを記載します。各項目には根拠となるファイルを併記しているので、値そのものを直すときはそのファイルを編集してから本書を更新してください。

## 1. 概要と目的

rAthena（GPL-3.0）による Ragnarok Online **Pre-Renewal** モードの検証・学習用サーバです。AWS Sandbox アカウント（`m3dc-sandbox` / 207567784705 / ap-northeast-1）上に Terraform で構築し、日本語 Windows クライアントから接続できるよう NPC・Mob 名・サーバメッセージの一部を日本語化しています。GitHub の RO-Labo リポジトリの `server/` として管理しています。Terraform state・`app/.env`・`backups/` は `.gitignore` で除外され、運用者の Mac にのみ存在します。

対象読者は SRE チームのメンバーです。初めてこのサーバに触る人が「今どうなっているか」を短時間で把握できることを目的としており、構築や日常運用の手順そのものは扱いません。

関連文書:

| 文書 | 内容 |
|---|---|
| [../README.md](../README.md) | 構築・運用・設定変更の手順（server の入口） |
| `docs/DESIGN.md` | 設計の背景・調査結果・決定理由（v0.5） |
| `docs/OPERATIONS.md` | 日常運用の runbook |
| `docs/TOOLS.md` | ツール一覧 |
| `docs/CHANGELOG.md` | 変更履歴 |
| [../../notes/archive/CLIENT_HANDOFF.md](../../notes/archive/CLIENT_HANDOFF.md) | HISTORICAL。旧ネイティブクライアント向け。実クライアントは RO-Labo の `client/README.md` |
| `docs/JP_GLOSSARY.md` / `docs/JP_TRANSLATION_RULES.md` / `docs/JP_NPC_PLAN.md` / `docs/JP_COVERAGE_PHASE2.md` | 日本語化の用語集・翻訳ルール・計画・棚卸し |
| [../../README.md](../../README.md) | RO-Labo 全体の入口 |
| [../../docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) | RO-Labo 全体アーキテクチャ・境界パラメータ・文字コード境界 |
| [../../docs/CURRENT_STATUS.md](../../docs/CURRENT_STATUS.md) | RO-Labo 現在地（PASS / PARTIAL / TODO / OUT OF SCOPE） |
| [../../client/README.md](../../client/README.md) | RO-Labo クライアント実装（SoT） |

## 2. ソフトウェア構成

| 項目 | 値 | 定義しているファイル |
|---|---|---|
| rAthena commit | `e985006171d2eb320ee512a653f4c83aea3d81b6`（master、2026-08-21） | `app/config.env`（`RATHENA_COMMIT`） |
| ビルドオプション | `./configure --enable-prere=yes --enable-packetver=20211103 && make server` | `app/rathena/Dockerfile` |
| ソース改変 | なし（rAthena 本体は無改変。差分は `conf/import/` と `overlay-utf8/` のみ） | — |
| PACKETVER | `20211103`（kRO 2021-11-03 RagexeRE 系、`PACKETVER_RE` 有効） | `app/config.env`（`PACKETVER`） |
| パケット暗号化 | 無効（キー 0 固定、2018-03-07 以降のクライアント仕様） | rAthena 本体（無改変） |
| サーバ名 | `rAthena-PreRE`（クライアントのサーバ一覧表示名） | `app/config.env`（`SERVER_NAME`） |
| ポート | login 6900 / char 6121 / map 5121。web-server（8888）は起動しない | `app/docker-compose.yml` |
| MariaDB | `mariadb:11.4`、DB `ragnarok`、`--character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci` | `app/config.env`、`app/docker-compose.yml` |
| rAthena 側の接続文字コード | `default_codepage` / `login_codepage` / `ipban_codepage` / `log_codepage` = `cp932` | `app/rathena/conf/import/inter_conf.txt.tmpl` |
| rAthena 主要テーブル | MyISAM（上流 `sql-init/01-main.sql` どおり、変更なし） | `app/rathena/sql-init/01-main.sql` |
| Docker Compose | v5.5.1（AL2023 同梱は非対応バージョンのため個別導入） | `terraform/user_data.sh.tftpl` |
| Docker Buildx | v0.37.1（Compose v5 の `build` は buildx ≥ 0.17 を要求。AL2023 同梱の 0.12 系では不可） | `terraform/user_data.sh.tftpl` |
| コンテナイメージ | `rathena:prere`（自作、multi-stage: builder `ubuntu:24.04` → runtime `ubuntu:24.04`） | `app/rathena/Dockerfile` |
| OS（EC2） | Amazon Linux 2023 x86_64（AWS 公開 SSM パラメータの最新版） | `terraform/data.tf` |
| DB スキーマの出所 | `sql-files/main.sql` / `logs.sql` / `roulette_default_data.sql` / `web.sql` は rAthena 上流の無改変コピー | `app/rathena/sql-init/01〜04-*.sql`、`app/rathena/RATHENA_SQL_SOURCE.md` |

## 3. ネットワークと公開範囲

| 項目 | 値 | 定義しているファイル |
|---|---|---|
| Internet へ公開するポート | TCP 6900（login）/ 6121（char）/ 5121（map）、いずれも `0.0.0.0/0` | `terraform/security.tf`（`var.service_ports`） |
| 非公開 | 22（SSH）、3306（MariaDB）。SG に ingress ルールが無い。MariaDB は `docker-compose.yml` で `ports:` 未定義 | `terraform/security.tf`、`app/docker-compose.yml` |
| web-server（8888） | 起動していない（`docker-compose.yml` に該当サービスが無い） | `app/docker-compose.yml` |
| Security Group | `sg-080a678ceda19ff70`（`legacy-app-lab-sg-verify`）、egress は all | `terraform/security.tf` |
| EIP（固定 Public IP） | `54.65.172.5` | `terraform/main.tf`（`aws_eip.app`） |
| Public DNS | `ec2-54-65-172-5.ap-northeast-1.compute.amazonaws.com` | AWS 側の自動割当 |
| 管理経路 | SSM Session Manager / Run Command のみ（Inbound 不要、22 番なし） | `terraform/iam.tf`（`AmazonSSMManagedInstanceCore`） |
| dockerd | unix socket のみ（TCP 公開なし） | Docker 既定 |

## 4. AWS リソース一覧

対象アカウント: `m3dc-sandbox`（207567784705）/ ap-northeast-1。命名規則: `legacy-app-lab-<summary>-<type>-verify`（AWS 側にゲーム固有語を出さない方針。アプリ内部は本来の技術名称のまま）。

### 4.1 タグ（`terraform/locals.tf` の `common_tags`。`provider.default_tags` で全リソースへ自動付与）

| タグ | 値 |
|---|---|
| `DoNotNuke` | `true`（aws-nuke 除外の必須タグ） |
| `SystemName` | `legacy-app-lab` |
| `SystemCode` | `00-01-01`（暫定値） |
| `Env` | `verify` |
| `Owner` | `sre` |
| `CodeRepository` | `local`（タグ値。リポジトリ公開後も未更新、変更には apply が必要） |
| `RootModulePath` | `terraform` |

`default_tags` が伝播しない箇所（EC2 の `root_block_device`、ENI、DLM の `tags_to_add`）には `common_tags` を明示的に merge している（`terraform/main.tf`、`terraform/backup.tf`）。

### 4.2 Terraform state のリソース（47 件）

| 分類 | 個数 | 主なリソース（Terraform アドレス） | 対応する `terraform/*.tf` |
|---|---:|---|---|
| データソース | 7 | `data.archive_file.app`、`data.aws_caller_identity.current`、`data.aws_iam_policy_document.*`（3 件）、`data.aws_region.current`、`data.aws_ssm_parameter.al2023` | `data.tf`、`iam.tf` |
| ネットワーク | 9 | `aws_vpc.main`、`aws_subnet.public`、`aws_internet_gateway.main`、`aws_route.public_default`、`aws_route_table.public`、`aws_route_table_association.public`、`aws_default_route_table.default`、`aws_default_security_group.default`、`aws_default_network_acl.default` | `network.tf` |
| セキュリティグループ | 5 | `aws_security_group.app`、`aws_vpc_security_group_ingress_rule.app["6900"\|"6121"\|"5121"]`（3 件）、`aws_vpc_security_group_egress_rule.all` | `security.tf` |
| EC2 / EBS / EIP | 13 | `aws_instance.app`、`aws_ebs_volume.data`、`aws_volume_attachment.data`、`aws_eip.app`、`aws_eip_association.app`、`aws_ec2_tag.primary_eni[...]`（`DoNotNuke`/`SystemName`/`SystemCode`/`Env`/`Owner`/`CodeRepository`/`RootModulePath`/`Name` の 8 件） | `main.tf` |
| IAM | 6 | `aws_iam_role.ec2`、`aws_iam_role_policy.ec2_inline`、`aws_iam_role_policy_attachment.ssm_core`、`aws_iam_instance_profile.ec2`、`aws_iam_role.dlm`、`aws_iam_role_policy_attachment.dlm` | `iam.tf` |
| CloudWatch | 2 | `aws_cloudwatch_log_group.containers`、`aws_cloudwatch_metric_alarm.status_check` | `cloudwatch.tf` |
| デプロイ | 4 | `aws_s3_bucket.deploy`、`aws_s3_bucket_server_side_encryption_configuration.deploy`、`aws_s3_object.app`、`aws_ssm_association.app_deploy` | `deploy.tf` |
| バックアップ | 1 | `aws_dlm_lifecycle_policy.data` | `backup.tf` |

主要リソースの名前と役割:

| リソース | 名前 | 役割 |
|---|---|---|
| VPC | `legacy-app-lab-vpc-verify` | 10.90.0.0/16、DNS hostnames 有効、IPv6 なし |
| Public Subnet | `legacy-app-lab-public-1a-subnet-verify` | 10.90.0.0/24、ap-northeast-1a、auto-assign 無効（EIP を明示付与） |
| EC2 | `legacy-app-lab-ec2-verify`（`i-03f3599d032bd7000`） | t3.medium、AL2023 x86_64、IMDSv2 必須（hop limit 1）、`credit_specification.cpu_credits = "unlimited"` |
| root EBS | `legacy-app-lab-root-ebs-verify` | gp3 30GB、暗号化、`delete_on_termination = true` |
| data EBS | `legacy-app-lab-data-ebs-verify` | gp3 20GB、暗号化、`/dev/sdf` → XFS → `/srv/ro-server` |
| EIP | `legacy-app-lab-eip-verify` | `54.65.172.5` |
| IAM ロール（EC2） | `legacy-app-lab-ec2-role-verify` | `AmazonSSMManagedInstanceCore` + インライン（CloudWatch Logs 書き込み、配布バケット `GetObject`、`ssm-output/` への `PutObject`） |
| CloudWatch Log Group | `legacy-app-lab-containers-cw-verify` | ストリーム login-server / char-server / map-server / mariadb、保持 14 日（`var.log_retention_days`） |
| CloudWatch Alarm | `legacy-app-lab-statuscheck-cw-verify` | `StatusCheckFailed_System` ≥ 1（2 期間）→ `ec2:recover` |
| S3 | `legacy-app-lab-deploy-s3-verify` | 配布用バンドル（キー `app.zip`、`local.deploy_object_key`）と SSM 実行ログ（`ssm-output/`）の一時置き場。SSE-S3、`force_destroy`。中身は aws-nuke で毎晩消える（§4.3） |
| SSM Association | `legacy-app-lab-app-deploy-verify`（`87ae7b16-2c1d-44e6-aeda-810462ffe1d8`） | `AWS-RunShellScript`。バンドル md5 を commands に含み app/ 変更で自動再実行。EC2 側で `/var/lib/ro-server/deployed.md5` と比較する冪等ガードあり |
| DLM ポリシー | `legacy-app-lab-data-dlm-verify` | data EBS（`DlmBackup=legacy-app-lab-data-verify` タグ）を 19:30 UTC（04:30 JST）に日次スナップショット、7 世代保持。`copy_tags = false`（有効にすると `Name` 重複で `CreateSnapshot` が失敗するため）、`tags_to_add` に `common_tags` を明示 |

### 4.3 aws-nuke との関係

| 項目 | 内容 |
|---|---|
| 実行体 | ekristen/aws-nuke v3.46.1、毎日 05:00 JST（EventBridge） |
| 除外条件 | `tag:DoNotNuke=true`（`__global__` フィルタ、全リソースタイプ共通） |
| 例外1: `EC2InternetGatewayAttachment` | 自身のタグを持たず放置すると毎晩 IGW がデタッチされるため、`docs/nuke/` の nuke-config に `tag:vpc:DoNotNuke` / `tag:igw:DoNotNuke` のフィルタを追記して除外済み |
| 例外2: `S3Object` | タグで保護できず、配布バケットの中身（`app.zip`、SSM 実行ログ）は毎晩削除される。`terraform apply` のたびに Terraform が再アップロードする前提で運用（永続データを置かない） |
| 既知の無害な事象: `EC2NetworkInterface` | v3.46.1 は ENI のタグを読まないため dry-run で EC2 プライマリ ENI が削除候補に出るが、プライマリ ENI（device index 0）は AWS 仕様上デタッチ不可のため実害なし |
| Terraform state | ローカル保持（S3 backend は S3Object 削除の影響を受けるため不使用） |

## 5. EC2 内部構成

### 5.1 ディレクトリ

```
/srv/ro-server/                    ← data EBS（XFS）
├── app/                           ← Compose プロジェクト（ローカル repo の app/ と 1:1、SSM が同期）
│   ├── docker-compose.yml, config.env, .env（秘密、EC2 上で生成、0600）
│   ├── rathena/                   ← Dockerfile, entrypoint.sh, conf/import/*, sql-init/*, overlay-utf8/
│   ├── scripts/                   ← deploy.sh, init-env.sh, update-public-ip.sh, backup-db.sh, restore-db.sh,
│   │                                  create-account.sh, set-password.sh, set-birthdate.sh, list-accounts.sh, status.sh
│   └── systemd/                   ← ro-server.service, ro-server-backup.{service,timer}
├── mariadb/                       ← MariaDB データ（bind mount）
└── backups/                       ← mariadb-dump（gzip）、7 日ローテーション
/opt/ro-server -> /srv/ro-server/app
/var/lib/ro-server/bootstrap.done  ← user-data 完了マーカー
/var/lib/ro-server/deployed.md5    ← 配布済みバンドルの md5（冪等ガード）
```

### 5.2 systemd

| Unit | 種別 | 内容 |
|---|---|---|
| `ro-server.service` | oneshot, `RemainAfterExit=yes` | `ExecStartPre=update-public-ip.sh`（IMDSv2 から Public IP を取得し `.env` に反映）→ `ExecStart=docker compose up -d --remove-orphans`。EC2 起動時に自動実行（`WantedBy=multi-user.target`） |
| `ro-server-backup.service` | oneshot | `backup-db.sh` を実行 |
| `ro-server-backup.timer` | timer | `OnCalendar=*-*-* 04:00:00 Asia/Tokyo`、`Persistent=true` |

### 5.3 Docker Compose サービス（`app/docker-compose.yml`）

| サービス | イメージ | ポート | `depends_on` / healthcheck | 備考 |
|---|---|---|---|---|
| `mariadb` | `mariadb:11.4` | 非公開 | healthcheck: `healthcheck.sh --connect --innodb_initialized`（10s 間隔、30 回、start_period 120s） | `sql-init/` を `docker-entrypoint-initdb.d` に ro マウント（初回のみ実行） |
| `login-server` | `rathena:prere`（`build` 定義はここのみ） | `6900:6900` | `mariadb` が healthy を待機。healthcheck: `</dev/tcp/127.0.0.1/6900`（30s start_period） | |
| `char-server` | 同上 | `6121:6121` | `login-server` が healthy を待機。healthcheck 同様 | |
| `map-server` | 同上 | `5121:5121` | `char-server` が healthy を待機。healthcheck start_period 180s（マップ/NPC 読み込みに時間がかかるため） | |

共通設定: `restart: unless-stopped`、`init: true`、`security_opt: no-new-privileges:true`、`cap_drop: ALL`、実行ユーザーは Dockerfile の `USER rathena(1000)`（root では動かさない）、`logging.driver: awslogs`（dual logging により `docker compose logs` も見える）。

### 5.4 entrypoint の描画

`app/rathena/Dockerfile` の runtime ステージで `conf/import/*.tmpl`（`char_conf.txt.tmpl` / `map_conf.txt.tmpl` / `inter_conf.txt.tmpl`）を配置し、コンテナ起動時に entrypoint が `envsubst` で実ファイル（`.tmpl` を除いた同名ファイル、モード 0600）へ描画してから `exec ./<role>-server` する。コンソールログは entrypoint 側で CP932 → UTF-8 に変換してから標準出力へ流すため、CloudWatch や `docker compose logs` でも日本語 NPC 名・キャラ名が読める。

## 6. rAthena 設定

すべて `app/rathena/conf/import/` に置き、rAthena 本体の conf は無改変です（各ファイルの末尾で import される仕組みを利用）。`.tmpl` 拡張子のファイルは entrypoint が `envsubst` で描画してから使われます。

### 6.1 倍率（`battle_conf.txt`、100 = 等倍）

| 項目 | 設定キー | 値 | 意味 |
|---|---|---|---|
| Base EXP | `base_exp_rate` | `10000` | 100 倍 |
| Job EXP | `job_exp_rate` | `10000` | 100 倍 |
| MVP 撃破ボーナス EXP | `mvp_exp_rate` | `10000` | 100 倍 |
| クエスト報酬 EXP | `quest_exp_rate` | `10000` | 100 倍 |
| 通常 Mob の一般/回復/消耗/装備アイテム | `item_rate_common` / `item_rate_heal` / `item_rate_use` / `item_rate_equip` | `500` | 5 倍 |
| Boss/MVP のカード以外（一般/回復/消耗/装備） | `item_rate_common_boss` / `_mvp`、`item_rate_heal_boss` / `_mvp`、`item_rate_use_boss` / `_mvp`、`item_rate_equip_boss` / `_mvp` | `10000` | 100 倍 |
| カード（通常/Boss/MVP 共通） | `item_rate_card` / `item_rate_card_boss` / `item_rate_card_mvp` | `100000` | 1000 倍（例: 0.01% のカードが 10.00%） |
| MVP 報酬アイテム / 追加ドロップ / 宝箱 | `item_rate_mvp` / `item_rate_adddrop` / `item_rate_treasure` | `10000` | 100 倍 |
| ドロップ率の上限 | `item_drop_*_max`（既定値、上書きなし） | `10000` | 100% 頭打ち |
| その他 | 変更なし | `100`（既定） | 等倍。`drops_by_luk: 0`、`rare_drop_announce: 0`、`item_logarithmic_drops: no`（線形） |
| Mob 表示名 | `override_mob_names` | `2` | 常に `mob_db` の `JapaneseName` を使用（`db/import/mob_db.yml` 215 件を日本語化。未収録は英語名にフォールバック） |

### 6.2 char 設定（`char_conf.txt.tmpl`）

| 項目 | 値 | 意味 |
|---|---|---|
| `pincode_enabled` | `no` | PIN コード入力なし（rAthena 既定は `yes`） |
| `server_name` | `${SERVER_NAME}`（= `rAthena-PreRE`） | クライアントのサーバ一覧表示名 |
| `char_ip` | `${PUBLIC_IP}` | クライアントが char-server へ接続する先（EIP） |
| `char_name_option` | `2` | 「禁止リスト」方式（`char_name_letters` に列挙した文字を禁止し、それ以外は許可） |
| `char_name_letters` | `!"#$%&'()*+,/:;<=>?` | 禁止記号。CP932 の 2 バイト目（0x40-0x7E, 0x80-0xFC）と衝突しない 0x21-0x3F の記号のみ選定。`-` `.` 数字は許可、半角空白はトリム仕様のため実質禁止 |
| 名前の長さ | `NAME_LENGTH = 24`（23 バイト、rAthena 既定） | 全角 11 文字まで、最小 4 バイト（全角 2 文字） |
| `char_del_option` | `2` | 削除確認は生年月日（`login.birthdate`）照合。PACKETVER 20211103 のクライアントは `char_del_option` の値に関係なく必ずこの経路 |
| `char_del_delay` | `0` | 削除予約から確定までの待ち時間なし（rAthena 既定 86400 秒） |
| `char_del_restriction` | `3` | パーティ / ギルド所属中は削除不可 |
| `start_point_pre` | 既定のまま | `new_1-1`〜`new_5-1,53,111`（初心者修練場の出現地点） |

### 6.3 login 設定（`login_conf.txt`）

| 項目 | 値 | 意味 |
|---|---|---|
| `new_account` | `no` | `_M`/`_F` による野良アカウント登録を無効化。アカウントは `create-account.sh` で作成 |
| `log_login` | `yes` | ログイン操作を `loginlog` テーブルへ記録（動的パスワード失敗 BAN の前提） |

### 6.4 log 設定（`log_conf.txt`）

| 項目 | 値 | 意味 |
|---|---|---|
| `sql_logs` | `yes` | ログを SQL テーブルへ記録（`no` の場合フラットファイル） |
| `log_commands` | `yes` | GM コマンドを `atcommandlog` へ記録（実際に記録されるのは `groups.yml` で `LogCommands: true` のグループのみ） |

### 6.5 inter 設定（`inter_conf.txt.tmpl`）と文字コード

| 項目 | 値 | 意味 |
|---|---|---|
| `default_codepage` | `cp932` | map-server / char-server の DB 接続文字コード |
| `login_codepage` / `ipban_codepage` / `log_codepage` | `cp932` | login-server 側の各接続（login / ipban / log は別接続のため個別指定） |
| `*_server_ip` | `mariadb`（compose サービス名） | login / ipban / char / map / web / log の 6 用途とも同じ MariaDB を参照 |

MariaDB のテーブル文字コードは `utf8mb4` / `utf8mb4_general_ci`（保存は UTF-8）。rAthena からの接続だけ `cp932` を指定し、CP932 ⇄ UTF-8 の変換は MariaDB 側（セッショントラッキング）に任せている。rAthena ソースは無改変。

### 6.6 GM グループ

`conf/groups.yml`（rAthena 本体の既定ファイル、overlay で上書きしていない）の `Id: 99`「Admin」を使用。`all_commands: true`、`LogCommands: true`。GM コマンドは `atcommandlog` テーブルに記録される（2026-09-24 時点 0 件）。

## 7. アカウントとキャラクター

### 7.1 作成・変更スクリプト

| スクリプト | 経路 | 内容 |
|---|---|---|
| `scripts/create-account.sh <userid> <M\|F> [group_id]`（Mac） → `app/scripts/create-account.sh`（EC2） | Mac → SSM Run Command → EC2 | `userid` は `^[A-Za-z0-9_]{4,23}$`、性別 `M`/`F`、`group_id` は 0〜99 の整数（既定 0、GM は 99）。`login.userid` に重複があれば作成前に中止 |
| `scripts/set-password.sh <userid>` | Mac → SSM、または `ssm-shell.sh` で対話実行 | `RO_PASSWORD` 環境変数の値で更新。SSM の実行パラメータに残したくない場合は `ssm-shell.sh` 経由の対話実行（無エコー入力） |
| `scripts/set-birthdate.sh <userid> [YYYY-MM-DD]` / `--all-missing` | Mac → SSM | 生年月日の設定。`--all-missing` は NULL のアカウントへ一括で既定値を設定（`account_id = 1` は対象外） |
| `scripts/list-accounts.sh` | Mac → SSM | アカウント一覧の確認 |

### 7.2 パスワード方針

`RO_PASSWORD` を指定しない場合、`app/scripts/create-account.sh` が英数字 12 桁（`openssl rand -base64` から `A-Za-z0-9` のみ抽出）を生成し、**作成時に 1 回だけ**標準出力へ表示する（再表示不可）。`use_MD5_passwords: no` のため `login.user_pass` には平文で保存される。`RO_PASSWORD` を指定した場合は SSM の実行パラメータに値が残る点に注意（残したくない場合は `ssm-shell.sh` 経由の対話実行を使う）。

### 7.3 生年月日 = キャラクター削除の確認コード

`login.birthdate` は既定 `2000-01-01`（`RO_BIRTHDATE='YYYY-MM-DD'` で作成時に変更可）。PACKETVER 20211103 のクライアントはキャラクター削除の確認にメールアドレスではなく生年月日（`YYYYMMDD`、サーバには下 6 桁 `YYMMDD` が届く）を使うため、`login.birthdate` が NULL だと削除できない。既存アカウントには `set-birthdate.sh` で設定する。

### 7.4 既存アカウント一覧（種別のみ、秘密情報なし）

| `account_id` | `userid` | 種別 | `group_id` | 備考 |
|---:|---|---|---:|---|
| 1 | — | inter-server 用システムアカウント（`sex='S'`） | — | 通常運用では触らない |
| 2000000 | `admin01` | GM | 99 | 未ログイン |
| 2000001 | `player01` | 一般 | 0 | ユーザーの検証用 |
| 2000002 | `deltest01` | 一般 | 0 | キャラクター削除検証用に作成。キャラクター 0 体、残置 |

3 件とも `birthdate` は `2000-01-01`。初期パスワードは最終レビュー時にローテーション済みで記録がないため、利用前に `set-password.sh` で設定する。

### 7.5 キャラクター削除の仕様

PACKETVER 20211103 クライアント（roBrowserLegacy 含む）は削除予約パケット 0x0827 → 生年月日 `YYMMDD` で確定する 0x0829 の 2 段階で削除する。rAthena `chclif_parse_char_delete2_accept`（`src/char/char_clif.cpp`）は `char_del_option` の値に関係なく `login.birthdate` と照合する（email 判定が効くのは 0x0068 / 0x01fb を送る旧クライアントのみ）。roBrowserLegacy の確認ダイアログ文言は msgstringtable #19「登録メールアドレス…」のままだが、入力欄は生年月日入力（#1815）であり `YYYYMMDD` を入力すると下 6 桁が送られる。パーティ / ギルド所属中は `char_del_restriction: 3` により削除不可。2026-09-24 に実クライアントで削除成功を確認済み。

検証ツール: `tools/chardel_probe.py`（Python 標準ライブラリのみ）。login → char → map を実パケットで実行し、`--create` / `--delete` / `--enter-map` / `--npc-skip <job|decline|cancel>` / `--cancel-reservation` を検証できる。パスワードは環境変数 `RO_PROBE_PASSWORD` で渡す。**EC2 内から `--host 127.0.0.1` で実行すること**（Mac から EIP 越しだと同一 char セッションの 3 回目の応答が届かない事象を確認済み）。

## 8. 日本語化

### 8.1 設計

Git リポジトリは UTF-8 / LF / BOM なしで管理し（`app/rathena/overlay-utf8/`）、Docker イメージのビルド時に `iconv` で CP932 へ変換して `/opt/rathena` に配置する（`app/rathena/Dockerfile`）。クライアントは `langtype 2`（CP932）。コンソールログは entrypoint で CP932 → UTF-8 に変換してから出力する。翻訳はすべて独自訳（jRO 公式文の転載なし）。

### 8.2 対象と現状の数値（2026-09-24）

| 項目 | 値 | 定義しているファイル |
|---|---:|---|
| MANIFEST エントリ数 | 148（上流差し替え 146 + 追加のみ 2） | `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv` |
| 翻訳版 NPC ファイル数 | 148 | `app/rathena/overlay-utf8/npc/` 配下 |
| 翻訳 `mes` 行数 | 49,578 行 | MANIFEST 対象ファイル群 |
| Mob 日本語名 | 215 件 | `app/rathena/overlay-utf8/db/import/mob_db.yml` |
| サーバメッセージ日本語化 | 214 件 | `app/rathena/overlay-utf8/conf/msg_conf/import/map_msg_eng_conf.txt` |
| NPC 総数（ロード時） | 13,043（上流 13,037 + 独自追加 6） | map-server 起動ログ `Done loading 'N' NPCs` |
| 頭上表示名の日本語化 | 可視 NPC 1,108 体中 1,099 体 | `docs/jp-npc-names.tsv` |

`Global_Functions.txt` は上流を残したまま 3 関数だけ同名上書きする「追加のみ」の扱い（`delnpc` すると `F_x()` の直接呼び出しがパース時エラーになるため）。

### 8.3 MANIFEST / 生成 conf の仕組み

`MANIFEST.tsv`（TAB 区切り: 上流パス／翻訳版パス。追加のみの NPC は上流パス欄に `-`）が Source of Truth。`tools/gen-jp-conf.py` がこれを読み、`app/rathena/overlay-utf8/npc/scripts_custom.conf` の `BEGIN JP OVERLAY`〜`END JP OVERLAY` ブロック（`delnpc:` / `npc:` 行）を生成する。手で conf を編集せず、MANIFEST に 1 行足してから生成し直す運用。

### 8.4 頭上表示名方式

`日本語#suffix::旧フル名` 形式（rAthena は `exname` だけで NPC を参照するため、表示名だけを日本語化して `exname` は不変に保てる）。`docs/jp-npc-names.tsv` が Source of Truth、`tools/jp_npc_names.py inventory` / `apply` / `check` で棚卸し・適用・整合検査を行う。

### 8.5 検証ツール

| ツール | 検査内容 |
|---|---|
| `scripts/check-jp-structure.sh`（`tools/jp_structure_check.py`） | エンコーディング、添字式内のエスケープ、添字走査（1c、後述の制約(1)）、トークン構造、ヘッダ、文字列、外部参照、`mes` 件数の一致 |
| `scripts/check-overlay.sh` | BOM の有無、CP932 への変換可否、改行コード（LF のみ）、禁止文字（U+301C 波ダッシュ。代わりに全角チルダ U+FF5E を使用） |
| `tools/jp_english_audit.py` | 翻訳済みファイルに残る英語文字列の機械監査（許容リストは `docs/jp-english-allowlist.tsv`） |
| `scripts/local-smoke.sh --expect-npcs 13043` | colima でクリーン起動し、NPC 総数とエラー 0 件を判定（`[Info]` 行は数えない） |
| `tools/jp-backup.sh` / `tools/jp-restore.sh` | 翻訳作業前後のスナップショット取得・復元 |

### 8.6 意図的に英語のまま

`getitemname()` のアイテム名、`item_db` の `Name`、Mob 表示名引数、`Karvodailnirol` / `Detrimindexta`、錬金術師のアナグラム・Lorem ipsum、モンクのラテン語、`tu_sword` の暗号パズル、URL、ステータス略語。`waitingroom` は日本語化済み。

### 8.7 未翻訳範囲

Pre-RE でロードされる 527 ファイル中 148 ファイルが対応済み。残りは主にフェイヨン系クエスト、転職導線の残り、日常 NPC の小物、Ep.10 以降の街クエスト（約 7 万 `mes`）、飛空艇・結婚・ミニゲーム・図書館・拡張職・WoE 城。GM コマンドの応答は英語のまま（`map_msg` は 214 件のみ翻訳）。

### 8.8 制約（4 点）

1. **添字式の走査バグ**: rAthena `parse_variable()` は添字式 `var[...]` 内を文字列やマルチバイト文字を意識せず生バイトで走査するため、CP932 で 2 バイト目が `[` / `]` になる文字（ー・ゼ・ゾ・‐ ほか計 104 字）が含まれると map-server が起動時に SIGSEGV で落ちる（再現はヒープ配置依存で不定）。検査 1c で検出し、該当箇所は英語表記にする。
2. **`Global_Functions.txt` の delnpc 不可**: `delnpc` すると `F_x()` の直接呼び出しがパース時スクリプトエラーになるため、追加のみ・同名上書きで対応。
3. **上流 NPC 名の非 ASCII**: `priest.txt` の cutin 名は `\x` エスケープで同一バイト列のため問題なし。`assassin_skills` の `¡¡#crypt` は全角スペースに改名して回避。
4. **自由入力クイズの日本語 IME 前提**: 吟遊詩人の歌詞当て、プロンテラの伝承歌、錬金術師スキル試験は日本語 IME 入力が前提で、サーバ側では対処できない。

## 9. 独自 NPC

上流 NPC の差し替えではなく、このサーバだけに追加した NPC。MANIFEST では上流パス欄が `-`。

### 9.1 サポート職員

| 項目 | 内容 |
|---|---|
| 位置 | `prontera,160,180`（噴水の南東） |
| ファイル | `app/rathena/overlay-utf8/npc/custom/jp/support.txt` |
| 条件 | 誰でも会話可能 |
| メニュー | (1) 体力/精神力の全回復（`percentheal 100,100`）、(2) 主要 8 都市（プロンテラ / ゲフェン / フェイヨン / モロク / アルベルタ / イズルード / アルデバラン / コモド）への無料ワープ、(3) サーバ説明（Pre-Renewal である旨、倍率の概要）、(4) やめる |
| 結果状態 | 選択に応じて全回復またはワープ。DB やキャラクターの永続状態は変えない |

### 9.2 冒険者支援員

| 項目 | 内容 |
|---|---|
| 位置 | `new_1-1`〜`new_5-1,58,114`（初心者修練場の出現地点 `53,111` のすぐ東、5 面すべてに `duplicate`） |
| ファイル | `app/rathena/overlay-utf8/npc/custom/jp/training_skip.txt`（テンプレート `冒険者支援員::TrainingSkipSupport`） |
| 条件 | `Class == Job_Novice` のみ（一次職以上・転生ノービス・養子は対象外。条件外だと「すでに職業についているため、このサービスは利用できません。」で終了） |
| 選択肢 | 剣士 / アーチャー / マジシャン / アコライト / 商人 / シーフ の一次職 6 職、または「まだ修練場を続ける」 |
| 処理手順 | (1) `NV_BASIC` を 9 に設定（未満の場合）→ (2) 未使用スキルポイントを 0 に → (3) `F_ClearJobVar` で転職クエスト変数を初期化 → (4) `callfunc "Job_Change"`（内部で `jobchange`）→ (5) `percentheal 100,100` + `sc_end SC_ALL` → (6) ノービスポーション（Id 569）10 個付与 → (7) `savepoint "prontera",117,72,1,1` → (8) `warp "prontera",150,180` |
| 結果状態 | 転職後は Job Lv 1 / Job Exp 0 / Basic Skill Lv 9（通常の一次職転職と同じ最終状態）。会話開始直後と選択後の 2 箇所で `Class != Job_Novice` を再確認し、二重転職を防止 |
| 検証状況 | 6 職・辞退・キャンセル・再訪拒否・再ログイン・実機接続でテスト済み（`tools/chardel_probe.py --npc-skip`、実クライアント） |

## 10. ログとバックアップ

### 10.1 ログ

| 種別 | 内容 |
|---|---|
| CloudWatch Logs | ロググループ `legacy-app-lab-containers-cw-verify`、ストリーム login-server / char-server / map-server / mariadb、保持 14 日。Info/Status 中心（login-server の「Closed connection from 127.0.0.1」は 10 秒ごとの healthcheck によるノイズ） |
| `docker compose logs` | awslogs と dual logging されているため EC2 上でも直接確認できる |
| `journalctl -u ro-server[.service\|-backup.service]` | systemd unit のログ |
| DB ログテーブル | `loginlog`、`charlog`、`atcommandlog`、`picklog`、`zenylog`、`npclog`、`mvplog`、`chatlog`、`branchlog`、`cashlog`、`feedinglog`、`interlog`（`app/rathena/sql-init/01-main.sql` / `02-logs.sql`） |
| Mac から | `scripts/logs.sh <service> [--since 1h] [--follow]`、`scripts/status.sh`、`scripts/verify.sh` |

### 10.2 バックアップ

| 種別 | 方法 | スケジュール / 保持 |
|---|---|---|
| DB ダンプ（自動） | `ro-server-backup.timer` → `mariadb-dump --single-transaction --quick --routines --events`（utf8mb4 接続） | 毎日 04:00 JST、`/srv/ro-server/backups/` に 7 日保持（`RETENTION_DAYS`） |
| DB ダンプ（即時） | `scripts/backup-db.sh`（Mac から SSM 経由） | 任意のタイミング。展開後 1KB 未満または `CREATE TABLE` を含まない場合は失敗扱い |
| DB リストア | `app/scripts/restore-db.sh <dump file>`（EC2 上・root） | login/char/map を停止 → リストア → 起動。`FORCE=1` で確認プロンプト省略 |
| EBS スナップショット（DLM） | `legacy-app-lab-data-dlm-verify` が `DlmBackup=legacy-app-lab-data-verify` タグの data EBS を対象に取得 | 毎日 19:30 UTC（04:30 JST）、7 世代、`copy_tags=false`（`tags_to_add` に `DoNotNuke` を含む common_tags を明示） |

## 11. 検証状況

| 検証 | 内容 | 状況 |
|---|---|---|
| ローカル smoke | `scripts/local-smoke.sh`（colima でクリーン起動、NPC 総数 13043・エラー 0 を判定） | NPC 翻訳ファイル追加のたびに実施 |
| CP932 往復テスト | `app/rathena/tests/cp932_roundtrip.c`（cp932 接続で INSERT → utf8mb4 接続で SELECT して一致確認。`ソ表能` の 0x5C 文字を含む） | PASS 確認済み |
| 実機テスト（サーバ側） | `tools/chardel_probe.py` による login→char→map のパケットレベル検証（キャラクター削除、map 入場、NPC 会話・転職） | EC2 内から実行し全段階成功（Mac から EIP 越しの実行は 3 回目応答が届かない既知の制約あり） |
| 実クライアント検証 | roBrowserLegacy（Web クライアント）でのログイン・日本語キャラ名作成・キャラクター削除（生年月日入力） | 2026-09-24 実施、シアレス作成・ユンヌ削除を確認。日本語チャットは未検証（`log_chat` 無効のためサーバ側に記録もない） |
| EC2 再起動後の復旧 | `aws ec2 reboot-instances` 後の `scripts/verify.sh` | 設計上自動復旧（`ro-server.service` が `enable` 済み） |

## 12. 既知の制約・未確認事項

- `SystemCode` は `00-01-01`（暫定値）。Sandbox 既存 SRE リソースの前例に合わせた値で、システム一覧ドキュメントへの正式登録は未確認。
- EC2 の `credit_specification.cpu_credits` は `unlimited`。標準的には `standard` が推奨だが、新規 t3 インスタンスの初回ビルド速度を優先して `unlimited` のまま。未変更。
- DLM が作成したスナップショットの実際の取得成功は、2026-09-24 04:30 JST 以降の分のみ未確認。
- ローカル検証用 DB（`app/.local/mariadb`、MyISAM）は不正終了すると crashed 扱いになることがあり、その場合はディレクトリごと削除して作り直す運用（自動修復の仕組みはない）。
- `terraform plan` で `aws_s3_object.app` の add 以外に add / destroy / replace が出た場合は apply しないこと（意図しない再作成の兆候）。
- 未翻訳範囲は §8.7 のとおり広く残っている。IME を使った日本語入力（キャラ名・ギルド名・パーティ名の作成 UI、チャット）はクライアント実機検証の対象で、クライアント実機検証の現在地は RO-Labo の [../../docs/CURRENT_STATUS.md](../../docs/CURRENT_STATUS.md) を参照。

## 13. 用語

| 用語 | 意味 |
|---|---|
| Pre-RE（Pre-Renewal） | 2008 年の「Renewal」アップデート以前のステータス/スキル計算式を使うゲームモード。1 次職・2 次職・転生まで実装され、3 次職は存在しない |
| PACKETVER | クライアントとサーバ間のパケット構造を決めるバージョン番号。本サーバは `20211103`（kRO 2021-11-03 RagexeRE 系） |
| exname | NPC の内部識別名（`::` の後ろに書く、または `script:exname` で指定）。`doevent` / `donpcevent` / `duplicate` などの参照キーになる。頭上表示名を変えても `exname` を変えなければ参照は壊れない |
| MANIFEST | `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv`。上流 NPC ファイルと翻訳版ファイルの対応表（Source of Truth）。`tools/gen-jp-conf.py` が読み込んで差し替え定義を生成する |
| overlay | `app/rathena/overlay-utf8/`。rAthena のディレクトリツリーを UTF-8 で持つ差分ツリー。ビルド時に CP932 へ変換されて `/opt/rathena` に重ねて配置される |
