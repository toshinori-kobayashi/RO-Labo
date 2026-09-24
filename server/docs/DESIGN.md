# Pre-Renewal 検証サーバ（rAthena）設計書

- 版: v0.5（2026-09-24 / キャラクター削除の生年月日方式、日本語化 第 2 フェーズ（頭上表示名・英語残り監査・追加翻訳）、独自 NPC「冒険者支援員」、倍率の再変更を §7・§10 に反映）
- 改版履歴: v0.3 → v0.4（2026-09-23、日本語化 §10 新設、初回 apply で判明した S3 公開ブロック（SCP）・buildx 要件を反映） / v0.4 → v0.5（2026-09-24、本改版）
- 対象: AWS Sandbox（m3dc-sandbox / 207567784705、ap-northeast-1）
- ゴール: サーバ側を完全稼働させ、クライアント担当へ `CLIENT_HANDOFF.md` で引き渡せる状態にする
- 命名方針: **AWS から見える名称は `legacy-app-lab` prefix の一般名称**に統一し、rAthena / Ragnarok Online 等のゲーム固有名は AWS リソース名・タグに出さない。アプリ内部（Docker / OS パス / DB / rAthena 設定）は本来の技術名称を維持する。

---

## 1. Sandbox 調査結果（設計の前提）

### 1.1 アカウントの現状（ap-northeast-1）

| 項目 | 結果 |
|---|---|
| VPC | **0 個**（default VPC も無し） → 新規 VPC を作る |
| 既存 EC2 / EIP | なし（EIP 上限 5、使用 0） |
| 孤立 IGW | `igw-00525c6f9dfd68e50`（`DoNotNuke=true`、VPC 無し）。他者の残骸なので**触らない** |
| S3 | `aws-nuke-config-...`（nuke 設定）、`m3dc-terraform-state-s3-sandbox`（空） |
| インスタンスタイプ | t3.medium は 1a/1c/1d で提供あり。vCPU クォータ 640 |
| AMI | Amazon Linux 2023 x86_64（SSM パラメータ `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`） |
| 自分の権限 | `PowerUserAccess` + `IAMFullAccess`。nuke の CodeBuild と EventBridge ルールは明示 Deny |

### 1.2 aws-nuke の仕組み

| 項目 | 結果 |
|---|---|
| トリガ | EventBridge `aws-nuke-daily`：`cron(0 20 ? * * *)` = **毎日 05:00 JST** |
| 実行体 | CodeBuild `aws-nuke-no-dry-run`（ekristen/aws-nuke **v3.46.1**）。`aws-nuke-run` は dry-run 用 |
| 設定 | `s3://aws-nuke-config-207567784705-ap-northeast-1/nuke-config.yaml` |
| 除外条件 | `__global__` フィルタ：**`tag:DoNotNuke` = `"true"`**（全リソースタイプ共通・追加マージ） |
| IAM 特例 | `IAMRolePolicy` / `IAMRolePolicyAttachment` は **ロール側のタグ**（`tag:role:DoNotNuke`）で判定 |
| 対象リージョン | ap-northeast-1 / ap-southeast-2 / us-east-1 / global |

### 1.3 aws-nuke の落とし穴と対処（ソースコードで確認済み）

`__global__` の `tag:DoNotNuke` フィルタは「そのリソース自身のタグ」を見る。以下は自身のタグを持たない。

| # | リソースタイプ | 事象 | 対処（実施済み） |
|---|---|---|---|
| A | **`EC2InternetGatewayAttachment`** | プロパティは `tag:vpc:*` / `tag:igw:*` のみ。放置すると**毎晩 IGW がデタッチ**される | **2026-09-22 に `nuke-config.yaml` へフィルタ追記済み**（`tag:vpc:DoNotNuke` / `tag:igw:DoNotNuke` = "true"）。dry-run で正常パース確認済み。原本と適用版は `docs/nuke/` に保全 |
| B | **`S3Object`** | タグプロパティ無し。**全バケットの全オブジェクトが毎晩削除**される（`nuke-config.yaml` のみキー名で除外） | S3 は**配布の一時置き場**（apply のたびに Terraform が再アップロード）にだけ使う。Terraform state・バックアップは S3 に置かない |
| C | `IAMInstanceProfileRole` | instance profile 側のタグで判定 | `default_tags` で instance profile にもタグが付くので OK |
| D | `EC2NetworkInterface` | Sandbox で稼働中の **v3.46.1 は ENI のタグをプロパティに出さない**（dry-run 実測: `DoNotNuke` 付きの ENI が `would remove` と表示）。ただし EC2 のプライマリ ENI（device index 0）は AWS 仕様でデタッチ不可のため削除は失敗し実害なし | 既知の無害なエラーとして許容。nuke ログに毎晩 `eni-…` の失敗が出る。恒久対処は aws-nuke 更新か `EC2NetworkInterface` に `property: VPC` 等の非タグフィルタ追加（要 Sandbox 管理者判断） |

> 別件の注意喚起: B により `m3dc-terraform-state-s3-sandbox` に置いた state も翌朝消える。

タグで守れることを確認したもの: VPC / Subnet / IGW / RouteTable / SG / SG Rule / EC2 / EBS Volume / EBS Snapshot / EIP / ENI / IAM Role / Instance Profile / CloudWatch LogGroup / CloudWatch Alarm / S3 Bucket。`SSMAssociation` は nuke の除外タイプ、DLM ポリシーは aws-nuke にリソースタイプ自体が無い（削除対象外）。

---

## 2. rAthena 調査結果

| 項目 | 結果 |
|---|---|
| commit | `e985006171d2eb320ee512a653f4c83aea3d81b6`（master、2026-08-21 "6th rebalance - Meister - Part 1 (#9997)"） |
| Pre-Renewal 化 | `./configure --enable-prere=yes`（公式。CI `build_servers_modes.yml` と同じ手順）。`src/config/renewal.hpp` の `PRERE` が定義され RENEWAL 系マクロが全て無効化される |
| Pre-RE データ | `db/pre-re/`（map_cache.dat 含む）を読み込み。NPC は `map.cpp:4264-4266` で **`npc/pre-re/scripts_main.conf` が自動選択**（設定変更不要）。3 次職 NPC は含まれない |
| PACKETVER | デフォルト **20211103**（CI テスト対象。`PACKETVER_RE` 扱い = kRO **2021-11-03 RagexeRE** 系クライアント） |
| パケット暗号化 | 2018-03-07 以降のクライアントは非暗号化（キー 0 固定）→ クライアント側の "Disable Packet Encryption" パッチ不要 |
| ビルド要件 | C++17。CI は Ubuntu 24.04 + `zlib1g-dev libpcre3-dev` + `mysql_config`（`libmariadb-dev-compat`） |
| Admin グループ | `conf/groups.yml` Id **99** "Admin"、Level 99、`all_commands: true`、`LogCommands: true`（標準のまま利用） |
| コマンドログ | `conf/log_athena.conf` デフォルトで `sql_logs: yes` / `log_commands: yes` → `atcommandlog` テーブルに記録 |
| 倍率の内部表現 | **全て percent（100 = 1 倍）**。線形（`item_logarithmic_drops: no`、`drops_by_luk: 0`）。上限 `item_drop_*_max: 10000`（= 100%） |
| アカウント登録 | `new_account: no` がデフォルト（`_M/_F` 登録は無効）→ アカウントはスクリプトで作成 |
| inter-server 認証 | デフォルト `s1/p1`（周知の値）→ 初期化時に生成値へ置換 |
| DB 初期化 | `sql-files/main.sql` + `logs.sql` + `roulette_default_data.sql` + `web.sql`（`use_sql_db: no` なので item/mob の SQL は不要）。この 4 ファイルは同コミットのものを `app/rathena/sql-init/` に vendoring |
| 起動ログ | "Pre-Renewal" と明示する行は無い。map-server の `Loading maps (using db/pre-re/map_cache.dat as map cache)` で判別する |

### 2.1 倍率設定値（`app/rathena/conf/import/battle_conf.txt`）

| 仕様 | 設定キー | 値 | 検算 |
|---|---|---|---|
| Base EXP 100 倍 | `base_exp_rate` | `10000` | 2026-09-24 に 1000 → 10000 |
| Job EXP 100 倍 | `job_exp_rate` | `10000` | 2026-09-24 に 1000 → 10000。MVP EXP / クエスト EXP（`mvp_exp_rate` / `quest_exp_rate`）も 10000 |
| 通常アイテム 5 倍 | `item_rate_common` / `item_rate_heal` / `item_rate_use` / `item_rate_equip` | `500` | 通常 Mob のみ |
| カード 1000 倍 | `item_rate_card` / `item_rate_card_boss` / `item_rate_card_mvp` | `100000` | 2026-09-24 に変更。Poring Card 0.01% → 10.00% |
| Boss / MVP のカード以外・MVP 報酬・追加ドロップ・宝箱 100 倍 | `item_rate_*_boss` / `item_rate_*_mvp` / `item_rate_mvp` / `item_rate_adddrop` / `item_rate_treasure` | `10000` | 2026-09-24 に等倍 → 100 倍 |
| その他 | 変更なし | `100` | 「原則標準」 |

---

## 3. AWS 構成

```
Internet
  │  TCP 6900 / 6121 / 5121 のみ（0.0.0.0/0）
  ▼
EIP  legacy-app-lab-eip-verify
  │
  ▼
VPC legacy-app-lab-vpc-verify (10.90.0.0/16, IPv4 のみ)
 └─ Public Subnet legacy-app-lab-public-1a-subnet-verify (10.90.0.0/24, ap-northeast-1a)
     └─ EC2 legacy-app-lab-ec2-verify (t3.medium / AL2023 / IMDSv2 必須)
         ├─ root EBS gp3 30GB  legacy-app-lab-root-ebs-verify
         ├─ data EBS gp3 20GB  legacy-app-lab-data-ebs-verify → /srv/ro-server
         └─ Docker Compose（内部名称は rathena / ro-server のまま）
             ├─ mariadb        (11.4 LTS, ポート非公開)
             ├─ login-server   :6900
             ├─ char-server    :6121
             └─ map-server     :5121
配布: S3 legacy-app-lab-deploy-s3-verify (app.zip) → SSM Association legacy-app-lab-app-deploy-verify
管理: SSM Session Manager / Run Command（Inbound 不要）
ログ: docker awslogs driver → CloudWatch Logs legacy-app-lab-containers-cw-verify
バックアップ: DLM legacy-app-lab-data-dlm-verify（data EBS 日次 7 世代）＋ EC2 内の mariadb-dump
```

### 3.1 作成する AWS リソース（Terraform、plan = 41）

| リソース | 名前 | 補足 |
|---|---|---|
| VPC | `legacy-app-lab-vpc-verify` | 10.90.0.0/16、DNS hostnames 有効、IPv6 なし |
| Subnet | `legacy-app-lab-public-1a-subnet-verify` | 10.90.0.0/24、auto-assign なし（EIP を付与） |
| IGW / Route Table | `legacy-app-lab-igw-verify` / `legacy-app-lab-public-rt-verify` | 0.0.0.0/0 → IGW |
| Default RT / SG / NACL | `legacy-app-lab-default-{rt,sg,nacl}-verify` | タグ付け目的。default SG のルールは空 |
| Security Group | `legacy-app-lab-sg-verify` | Ingress: TCP 6900/6121/5121 from 0.0.0.0/0（ルール名 `legacy-app-lab-{port}-sgr-verify`）。Egress: all |
| EC2 | `legacy-app-lab-ec2-verify` | t3.medium（unlimited）、AL2023 x86_64、IMDSv2 required（hop limit 1）、hostname `legacy-app-lab-verify` |
| EBS (root / data) | `legacy-app-lab-root-ebs-verify` 30GB / `legacy-app-lab-data-ebs-verify` 20GB | gp3、暗号化。data は `/dev/sdf` → XFS → `/srv/ro-server` |
| EIP | `legacy-app-lab-eip-verify` | 固定 Public IP。ENI にもタグ `legacy-app-lab-eni-verify` |
| IAM Role / Instance Profile | `legacy-app-lab-ec2-role-verify` | `AmazonSSMManagedInstanceCore` + インライン `legacy-app-lab-cwlogs-policy-verify`（CloudWatch Logs 書き込み・配布バケット GetObject・SSM 出力 PutObject） |
| CloudWatch Log Group | `legacy-app-lab-containers-cw-verify` | ストリーム: login-server / char-server / map-server / mariadb、保持 14 日 |
| CloudWatch Alarm | `legacy-app-lab-statuscheck-cw-verify` | StatusCheckFailed_System → EC2 自動復旧 |
| S3 Bucket | `legacy-app-lab-deploy-s3-verify` | 配布用 `app.zip`（`legacy-app-lab-app-bundle-verify`）と SSM 実行ログ。`force_destroy`、SSE-S3。公開ブロックは新規バケットの既定で全項目有効（この Sandbox は SCP で `s3:PutBucketPublicAccessBlock` を拒否するため Terraform では宣言しない。実効値は全 true を確認済み） |
| SSM Association | `legacy-app-lab-app-deploy-verify` | `AWS-RunShellScript`。バンドル md5 を含むため app/ 変更で自動再実行。apply は成功まで最大 50 分待機 |
| DLM Policy / Role | `legacy-app-lab-data-dlm-verify` / `legacy-app-lab-dlm-role-verify` | `DlmBackup=legacy-app-lab-data-verify` タグの EBS を 19:30 UTC（04:30 JST）に日次スナップショット、7 世代。スナップショット名 `legacy-app-lab-data-snapshot-verify`。タグは `tags_to_add` で明示（`copy_tags` は `Name` 重複で CreateSnapshot が失敗するため無効） |

### 3.2 タグ（`provider.default_tags` で全リソースに付与。root EBS / ENI / DLM スナップショットは明示付与）

| タグ | 値 |
|---|---|
| `DoNotNuke` | `true`（**必須**） |
| `SystemName` | `legacy-app-lab` |
| `SystemCode` | `00-01-01`（Sandbox 既存 SRE リソースの前例に合わせた暫定値） |
| `Env` | `verify` |
| `Owner` | `sre` |
| `CodeRepository` | `local`（リモートリポジトリ無し） |
| `RootModulePath` | `terraform` |
| `Name` | 各リソース名（§3.1） |

名称は `terraform/locals.tf` の `name_fmt = "${project_name}-%s-${environment}"` から `format()` で生成し、個別ハードコードはしない。`project_name` / `environment` は変数（default `legacy-app-lab` / `verify`）。

### 3.3 選定理由

- **t3.medium / unlimited**: rAthena 推奨 2 core / 2 GB を満たす。新規 t3 はクレジット残高ゼロから始まるため `standard` だと初回ビルドが数倍遅くなる。サープラス課金はビルド 1 回あたり数セント。月額目安: EC2 約 $40 + EBS 約 $5 + Public IPv4 約 $3.6 ≒ $50
- **単一 AZ / 単一 Public Subnet / IPv4 のみ**: 要件どおり最小構成。rAthena は IPv4 前提
- **Terraform state はローカル**: §1.3-B。`.terraform.lock.hcl` は Git 管理対象（provider 固定）
- **S3 + SSM Association による配布**: AWS 側を全て Terraform で宣言し、`terraform apply` 1 回で「インフラ作成 → アプリ配布 → ビルド → 起動」まで完結させる。SSH / rsync / CLI 手作業のデプロイ経路を持たない。`terraform destroy` で全て消える（DLM が作ったスナップショットだけは残る）

---

## 4. EC2 内部設計

### 4.1 ディレクトリ（データボリューム上）

```
/srv/ro-server/                  ← data EBS (XFS, label app-data)
├── app/                         ← Compose プロジェクト。ローカル repo の app/ と 1:1（SSM が同期）
│   ├── docker-compose.yml
│   ├── config.env               ← 非秘密の設定（Git 管理・単一の真実）
│   ├── .env                     ← 秘密情報（初回デプロイ時に自動生成、同期対象外、0600）
│   ├── rathena/                 ← Dockerfile, entrypoint.sh, conf/import/*, sql-init/*
│   ├── scripts/                 ← deploy.sh, init-env.sh, update-public-ip.sh, backup-db.sh, restore-db.sh, create-account.sh, list-accounts.sh, status.sh
│   └── systemd/                 ← ro-server.service, ro-server-backup.{service,timer}
├── mariadb/                     ← MariaDB データ（bind mount、uid 999）
└── backups/                     ← mariadb-dump（gzip）、7 日ローテーション
/opt/ro-server -> /srv/ro-server/app
/var/lib/ro-server/bootstrap.done  ← user-data 完了マーカー / deployed.md5 ← 配布済みバンドル
```

### 4.2 user-data（初回起動時のみ、`terraform/user_data.sh.tftpl`）

1. `dnf install docker git rsync xfsprogs unzip`、Docker 有効化、ec2-user を docker グループへ
2. Docker Compose plugin v5.5.1 と **Docker Buildx plugin v0.37.1** を GitHub Releases から取得（`checksums.txt` で sha256 検証、`/usr/local/lib/docker/cli-plugins/`）。AL2023 同梱の buildx は 0.12 系で Compose v5 の `build`（buildx ≥ 0.17 必須）が動かないため、探索順で優先されるパスに新しい版を置く
3. 4 GB swapfile
4. data EBS（`/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_vol...`、最大 10 分待機）→ 未フォーマットなら XFS → fstab（UUID, nofail）→ `/srv/ro-server`
5. ディレクトリ作成、`/opt/ro-server` シンボリックリンク、hostname、完了マーカー

### 4.3 配布（`terraform/templates/ssm_deploy.sh.tftpl` → `app/scripts/deploy.sh`）

1. SSM 側: 完了マーカーを最大 20 分待つ → 同じ md5 が配布済みでサービス稼働中なら終了（冪等ガード）→ S3 から `app.zip` 取得・md5 検証 → 一時展開 → `rsync -a --delete --exclude .env` で `/srv/ro-server/app` へ → `deploy.sh`
2. `deploy.sh`（root）: 権限整備 → `init-env.sh`（`.env` 生成/同期）→ `update-public-ip.sh`（IMDSv2 → `PUBLIC_IP`）→ systemd unit 配置・enable → `docker compose build --pull` → `systemctl restart ro-server` → `status.sh`

### 4.4 Docker Compose（`app/docker-compose.yml`）

| サービス | イメージ | ポート | 要点 |
|---|---|---|---|
| `mariadb` | `mariadb:11.4` | **公開なし** | `/srv/ro-server/mariadb` を bind mount。`sql-init/` を initdb に ro マウント（初回のみ実行）。`healthcheck.sh` |
| `login-server` | `rathena:prere`（自作） | `0.0.0.0:6900` | `build` 定義はここだけ。`depends_on: mariadb (healthy)` |
| `char-server` | 同上 | `0.0.0.0:6121` | `depends_on: login-server (healthy)` |
| `map-server` | 同上 | `0.0.0.0:5121` | `depends_on: char-server (healthy)`、start_period 180s |

共通: `restart: unless-stopped`、`init: true`、`logging: awslogs`（dual logging により `docker compose logs` も動く）、`no-new-privileges`、rAthena 3 サービスは `cap_drop: ALL`、`USER rathena(1000)`。privileged なし。

### 4.5 rAthena イメージ（`app/rathena/Dockerfile`）

- builder: `ubuntu:24.04` + `build-essential git zlib1g-dev libpcre3-dev libmariadb-dev libmariadb-dev-compat`。`git fetch --depth 1 origin ${RATHENA_COMMIT}` → `./configure --enable-prere=yes --enable-packetver=${PACKETVER}` → `make -j$(nproc) server`
- runtime: `ubuntu:24.04` + `libmariadb3 zlib1g libpcre3 gettext-base tzdata bash`。`/opt/rathena` に `login-server char-server map-server conf db npc log`。`conf/import` は `import-tmpl` を敷いてから本リポジトリの設定で上書き
- entrypoint: 必須環境変数を検証し、`envsubst` で `char/map/inter_conf.txt.tmpl` を描画（0600）→ `exec ./<role>-server`

### 4.6 rAthena 設定（全て `conf/import/`、本体 conf は無改変）

| ファイル | 内容 |
|---|---|
| `battle_conf.txt` | §2.1 の倍率 |
| `log_conf.txt` | `sql_logs: yes` / `log_commands: yes` |
| `login_conf.txt` | `new_account: no` / `log_login: yes` |
| `char_conf.txt.tmpl` | `userid`/`passwd`（生成値）、`server_name: rAthena-PreRE`、`login_ip: login-server`、`char_ip: ${PUBLIC_IP}`、`pincode_enabled: no` |
| `map_conf.txt.tmpl` | `userid`/`passwd`、`char_ip: char-server`、`map_ip: ${PUBLIC_IP}` |
| `inter_conf.txt.tmpl` | `*_ip: mariadb`、`*_id/_pw/_db` は `.env` の値 |
| `sql-init/99-interserver-account.sh` | initdb で source され、`login.account_id=1` を生成値へ UPDATE |

秘密（DB root / ragnarok パスワード、inter-server 認証）は EC2 上の `init-env.sh` が生成し `.env`（0600）にのみ保存。ローカル repo には `.env.example` だけ。

### 4.7 systemd

- `ro-server.service`: `ExecStartPre=update-public-ip.sh` → `docker compose up -d --remove-orphans` / `ExecStop=docker compose down`。EC2 再起動で自動復旧
- `ro-server-backup.timer`: 毎日 04:00 JST に `mariadb-dump --single-transaction` → `/srv/ro-server/backups/`、7 日保持

---

## 5. 運用フロー（ローカル Mac から）

前提ツール: `aws` CLI（SSO `sandbox-power`）、`terraform`、`session-manager-plugin`（導入済み 1.2.835.0）、`nc`、`python3`。

| 手順 | コマンド | 内容 |
|---|---|---|
| 構築・更新 | `terraform -chdir=terraform apply` | インフラ作成 + `app/` の配布 + ビルド + 起動。app/ を変更したら再 apply で再配布 |
| アカウント作成 | `scripts/create-account.sh <id> <M/F> [group]` | SSM Run Command 経由。GM は `99` |
| 疎通確認 | `scripts/verify.sh` | 6900/6121/5121 open・22/3306 closed の判定 + リモート `status.sh` |
| ログ | `scripts/logs.sh [service] [--since 1h] [--follow]` | CloudWatch Logs から取得 |
| シェル | `scripts/ssm-shell.sh` | Session Manager。`cd /opt/ro-server && docker compose ps|logs|restart|down|up -d` |
| バックアップ | DLM（自動）／`scripts/backup-db.sh`（即時 dump）／`app/scripts/restore-db.sh` | |
| 撤去 | `terraform -chdir=terraform destroy` | 全リソース削除（DLM 作成済みスナップショットは残る。不要なら手動削除） |

---

## 6. セキュリティ要件との対応

| 要件 | 対応 |
|---|---|
| 6900/6121/5121 を Internet へ公開 | SG ingress 3 本のみ |
| 22 / 3306 / Docker daemon 非公開 | SG に無し。MariaDB は `ports:` 未定義。dockerd は unix socket のみ |
| 管理は SSM | Session Manager / Run Command / State Manager。SSH 経路を持たない |
| rAthena を root で動かさない | `USER rathena(1000)`、`cap_drop: ALL`、`no-new-privileges` |
| privileged 不使用 | なし |
| 不要サービス | web-server(8888) は起動しない、管理 Web UI は追加しない |
| ログ確認 | CloudWatch Logs（4 ストリーム）＋ `docker compose logs`、OS は `journalctl`、配布ログ `/var/log/ro-server-deploy.log` |
| 認証情報を commit しない | `.env` は EC2 上で生成、`.gitignore` 済み。s1/p1 は初期化時に置換 |
| その他 | IMDSv2 必須（コンテナから到達不可）、EBS 暗号化、S3 公開ブロック、`ipban_enable: yes` |

---

## 7. 決定事項

| 項目 | 決定 | 理由 |
|---|---|---|
| PACKETVER | **20211103**（kRO 2021-11-03 RagexeRE） | rAthena デフォルト・CI テスト対象。変更は `app/config.env` の 1 行 + 再 apply |
| インスタンス | t3.medium x86_64 / AL2023 / unlimited | §3.3 |
| ボリューム | root 30GB + data 20GB（gp3、暗号化） | ビルドキャッシュと swap 4GB を見込む。data 分離で再作成・スナップショットが容易 |
| web-server | 起動しない | 8888 の追加公開が必要。エンブレム表示等に影響するが通常プレイには不要 |
| `pincode_enabled` | `no` | 検証時の摩擦低減。標準は `yes` |
| `new_account` | `no`（標準） | 野良登録を防ぐ。作成はスクリプト |
| `server_name` | `rAthena-PreRE` | 空白・記号入りはクライアント側のエンブレム処理で問題になる旨が rAthena の conf に明記 |
| Terraform state | ローカル | S3 が使えない（§1.3-B） |
| タグ | §3.2 | 会社ポリシーのキーを維持しつつ SystemName を一般名称に |
| キャラクター削除（生年月日方式） | `login.birthdate` に既定値（`create-account.sh` 既定 `2000-01-01`）を必ず設定し、`char_del_delay: 0` とする | PACKETVER 20211103 クライアント（roBrowserLegacy 含む）の削除確定（0x0829）は `char_del_option` の値に関係なく `login.birthdate` と照合される（`chclif_parse_char_delete2_accept`。email 判定が効くのは 0x0068/0x01fb を送る旧クライアントのみ）。birthdate が NULL だとこのクライアントからは削除不能なため、既定値の付与が必須（2026-09-23 判明・修正） |
| 日本語化 第 2 フェーズ・頭上表示名 | NPC ヘッダを `日本語#suffix::旧フル名` 方式に統一し、`::` 以降（exname）は変更しない | rAthena は NPC を exname のみで参照する（`npc_parsename`/`npcname_db`）。表示名だけを書き換えれば `doevent`/`donpcevent`/`enablenpc`/`disablenpc` 等の外部参照を壊さずに頭上表示を日本語化できる（詳細 §10.8） |
| `Global_Functions.txt` 追加のみ方式 | 上流ファイルを `delnpc` せず、翻訳版を「追加のみ」で末尾に読み込ませ同名関数を上書きする | `F_getpositionname()` 等は `callfunc` ではなく直接呼び出し構文で参照されており、パーサはパース時に関数定義の存在を要求する。上流を先に外すと未定義関数でスクリプトエラーになるため、上流を残したまま翻訳版で上書きする方式にした（詳細 §10.8） |
| 独自 NPC「冒険者支援員」の転職処理 | 一次職への転職時に `NV_BASIC`（Basic Skill）9 を付与し、未使用スキルポイントを 0 にする | `F_CanChangeJob`（転職可否判定）と `pc_calc_skilltree_normalize_job_sub`（スキルツリー正規化）が Basic Skill 9 を前提としており、修練場クリアによる通常の転職と同じ状態にしないと転職後の挙動が不整合になる |
| 倍率の再変更（2026-09-24） | Base/Job EXP を 10 倍→100 倍、MVP/クエスト EXP を等倍→100 倍、通常カードを 100 倍→1000 倍、Boss/MVP カードを 10 倍→1000 倍、Boss/MVP（カード以外）・MVP 報酬・追加ドロップ・宝箱を等倍→100 倍に変更。通常アイテム 5 倍は変更なし | 検証を短時間で回す（一次〜二次職・カード収集まで試す）ための倍率調整。現在値は §2.1 参照 |

---

## 8. 成功条件 → 確認方法

| # | 条件 | 確認方法 |
|---|---|---|
| 1-2 | EC2 / Compose 起動 | `scripts/verify.sh` → `docker compose ps`（4 サービス healthy/running） |
| 3-4 | MariaDB 起動・login-server の DB 接続 | login-server ログ `The login-server is ready` |
| 5-7 | char / map 起動、サーバ間通信 | char ログ `Connected to login-server`、map ログ `Connect success! (Map Server Connection)` / `Successfully logged on to Char Server` |
| 8-9 | Pre-Renewal 起動、Map/NPC/Mob ロード | map ログ `Loading maps (using db/pre-re/map_cache.dat ...)`、`Successfully loaded 'N' maps`、`Done loading 'N' NPCs` |
| 10 | DB 永続 | アカウント作成 → `systemctl restart ro-server` と EC2 再起動 → 行が残ること |
| 11-13 | GM / 一般アカウント、Group 99 | `scripts/create-account.sh`、`scripts/list-accounts.sh` で `group_id` 確認 |
| 14-16 | 倍率 | `battle_conf.txt` の値（クライアント完成後に `@mobinfo` 等で最終確認） |
| 17-19 | 到達性 | `scripts/verify.sh`（nc） |
| 20 | EC2 再起動後の復旧 | `aws ec2 reboot-instances` → 数分後に `scripts/verify.sh` |
| 21 | CLIENT_HANDOFF.md | 作成 |

---

## 9. リポジトリ構成（ローカルのみ、GitHub 管理なし）

注: 2026-09-24 以降、本リポジトリは RO-Labo の `server/` として GitHub 管理。以下は構築時点（ローカルのみ）の構成の記録。

```
ro-server/
├── README.md                # 構築・運用・倍率変更・アカウント作成・バックアップ（構築後に作成）
├── CLIENT_HANDOFF.md        # クライアント担当向け接続仕様（構築後に作成）
├── .gitignore
├── terraform/               # versions/providers/variables/locals/data/network/security/iam/cloudwatch/main/deploy/backup/outputs
│   ├── user_data.sh.tftpl
│   └── templates/ssm_deploy.sh.tftpl
├── app/                     # EC2 の /srv/ro-server/app と 1:1（Terraform が zip 化して配布）
│   ├── docker-compose.yml, config.env, .env.example
│   ├── rathena/             # Dockerfile, entrypoint.sh, conf/import/*, sql-init/*, overlay-utf8/(日本語オーバーレイ), tests/(CP932 往復テスト)
│   ├── scripts/             # EC2 上で動く運用スクリプト
│   └── systemd/
├── scripts/                 # ローカル Mac 用（SSM 経由のみ）: verify / logs / create-account / list-accounts / status / backup-db / ssm-shell
└── docs/                    # DESIGN.md（本書）, nuke/（nuke-config の原本と適用版）
```

---

## 10. 日本語化設計（初期構築から組み込む）

目標: 「日本語 Windows クライアント（kRO 2021-11-03 RagexeRE + 日本語データ）から、可能な限り日本語で Pre-Renewal を遊べる」。jRO の完全再現ではなく、rAthena Pre-Renewal を基準に日本語の表示・コミュニケーション・NPC 体験を整える。

### 10.1 前提となる実仕様（ソース・一次情報で確認）

| 事実 | 根拠 |
|---|---|
| クライアントは `langtype` で文字コードとフォント charset を決める。**`langtype 2`（= `servicetype japan`）で CP932 + SHIFTJIS_CHARSET** | クライアント再構築ソース `Framework/Locale.cpp` の `InitLanguage()`（`g_codePage = 932`）、WARP `FixFontsCharset` の charset テーブル（index 2 = 0x80 = SHIFTJIS_CHARSET） |
| `servicetype` と `langtype` は同じ内部変数 `g_serviceType` に入り、**両方書くと `langtype` が後勝ち** | 同 `SetOption()` → `SelectClientInfo()` の処理順 |
| クライアントは UTF-8 を解釈しない。rAthena も UTF-8 を扱わず**バイト列を素通し**する | `src/map/npc.cpp:5673-5679`（UTF-8 BOM を拒否し「クライアントは UTF-8 非対応」と明記） |
| rAthena のスクリプトパーサは Shift_JIS の 2 バイト目 0x5C（ソ・表・能・十・予・申 等）を壊さない | `src/map/script.cpp:1342`（直前バイトが 0x7E 以下のときだけ `\` をエスケープ扱い） |
| rAthena の DB 文字コード指定 `default_codepage` 等は `SET NAMES` を SQL で送るだけ（`src/common/sql.cpp:167-172`）。ただし **MariaDB 11.4 + libmariadb ではセッショントラッキングでクライアント側 charset も cp932 に追随する**ことを往復テストで実測（0x5C を含む「ソ表能」が壊れない）。したがってソースパッチは不要 | `app/rathena/tests/cp932_roundtrip.c`（両モード PASS） |
| 名前バリデーション `char_name_option` は**バイト単位**で `char_name_letters` と照合。既定 `1`（英数字のみ） | `src/char/char.cpp:1362-1371`、`conf/char_athena.conf:155-164` |
| `NAME_LENGTH = 24`（23 バイト） → CP932 で**全角 11 文字**。`char_name_min_length: 4` はバイト数 → 全角 2 文字 | `src/common/mmo.hpp:154` |
| Mob 名は**サーバが送る**。`override_mob_names: 2` で mob_db の `JapaneseName` を全 Mob に適用（スポーンファイル無改変）。クエスト UI の討伐対象名も `jname` | `conf/battle/monster.conf:120-123`、`src/map/npc.cpp:5366-5369`、`src/map/mob.cpp:454-456`、`clif_quest_add()` |
| NPC ファイルの差し替えは `npc/scripts_custom.conf`（`npc/pre-re/scripts_main.conf` の最後で import）で `delnpc:` → `npc:` すれば上流無改変で可能 | `src/map/map.cpp:4245-4250`、`src/map/npc.cpp:3632-3641` |
| サーバメッセージは `conf/msg_conf/import/map_msg_eng_conf.txt` で ID 単位に上書きできる（エスケープ処理なし・511 バイト） | `conf/msg_conf/map_msg.conf` 末尾、`src/common/msg_conf.cpp` |
| rAthena 内蔵の多言語（`@langtype`）に日本語は無い（`LANG_RUS/SPN/GRM/CHN/MAL/IDN/FRN/POR/THA` のみ） | `src/common/msg_conf.hpp` |
| jRO 公式クライアントは rAthena 非対応（パケットテーブルは kRO Ragexe/RagexeRE 系譜のみ） | `src/config/packets.hpp` |
| 2018-03-07 以降のクライアントはパケット暗号化なし → "Disable Packet Encryption" 不要 | `src/map/clif_obfuscation.hpp` |

### 10.2 責務分離（サーバ側 / クライアント側）

| 項目 | 文字列の所在 | 担当 | 本構成での対応 |
|---|---|---|---|
| NPC 会話 / Quest 会話 / 転職 NPC 会話 / Warp・システム NPC のメニュー | サーバの `npc/**/*.txt`（`mes`/`select`/`menu`）。**サーバから文字列そのものが送信される** | **サーバ** | `overlay-utf8/npc/custom/jp/` に翻訳版を置き `scripts_custom.conf` で差し替え。初期セット（当時）: カプラ機能・カプラ NPC・プロンテラ案内・1 次職転職 6 種（剣士/シーフ/マジシャン/アーチャー/アコライト/商人）・独自「サポート職員」。以降 Batch 1〜5・第 2 フェーズで対象を拡張済み。現在の対応ファイル数・範囲は `docs/SPEC.md` を参照。上記以外の NPC は**英語のまま**（同じ方式で追加可能） |
| サーバ送信のシステムメッセージ（`msg_txt`） | `conf/msg_conf/map_msg.conf`。サーバ送信 | **サーバ** | GM コマンド以外のコードから参照される **214 件**を日本語化（`map_msg_eng_conf.txt`）。GM コマンドの応答は英語のまま |
| broadcast / announce / `@` コマンドの文字列 | サーバ（バイト透過） | サーバ（透過） | GM がクライアントから日本語で入力すれば、そのまま CP932 で全員に配信される。スクリプトの `announce` も同様 |
| 独自 GM / イベント NPC | サーバ | サーバ | `overlay-utf8/` に **UTF-8 で書く**だけでビルド時に CP932 へ変換される |
| Item 名 / 説明、Skill 名 / 説明 | クライアントの `data/luafiles514/lua files/datainfo/`（itemInfo）、`skillinfoz/` | **クライアント** | サーバ側 `item_db.yml` / `skill_db.yml` の `Name` は GM コマンド・ログ・一部メッセージにしか出ない。今回は変更しない |
| Mob 名 | **サーバ送信**（`mob_db` の `JapaneseName`） | **サーバ** | `override_mob_names: 2` + `overlay-utf8/db/import/mob_db.yml`（当時の見込みは約 220 体、カタカナ転写。確定件数は `docs/SPEC.md` 参照）。未収録 Mob は英語 |
| Quest 名 / 本文 / Quest UI | クライアントの `data/questid2display.txt`。サーバ `quest_db.yml` の `Title` はサーバ内部用 | クライアント | 討伐対象 Mob 名だけはサーバの `jname` が使われる |
| Map 名 | クライアントの `data/mapnametable.txt` | クライアント | — |
| UI 全般・クライアント内蔵メッセージ | `data/msgstringtable.txt`、`UI\` の画像、`cardprefixnametable.txt` 等 | クライアント | `langtype 2` では `msgstringtable.txt` が既定で読まれる |
| フォント | クライアント | クライアント | `langtype 2` で charset は SHIFTJIS 固定。フェイスは WARP "Customize Font name"（MS ゴシック等） |
| 日本語入力（IME）/ チャット | クライアント内蔵 IME 処理 + サーバ透過 | クライアント（入力）/ サーバ（透過） | サーバは `clif_process_message` で長さのみ検証。**IME 実用性は実機検証が必要** |
| キャラクター名 / ギルド名 / パーティ名 | サーバのバリデーションと DB、クライアントの入力 UI | 両方 | サーバ: `char_name_option: 2` で許可、全角 11 文字まで。クライアント: 作成 UI で IME 入力できるか要検証 |

### 10.3 文字コード設計（UTF-8 を内部標準、CP932 は「実行時ファイルと通信」に限定）

```
Git リポジトリ            ビルド（Dockerfile）            rAthena 実行時               クライアント
app/rathena/overlay-utf8  ── iconv UTF-8→CP932 ──▶  /opt/rathena/{npc,conf,db}  ──▶  langtype 2 (CP932)
(UTF-8, BOM なし, LF)      失敗したらビルド失敗          （CP932 バイト列）             ◀── チャット/名前 (CP932)
                                                            │
                                     SET NAMES cp932（default_codepage）
                                                            ▼
                                        MariaDB 11.4: 文字コード変換 cp932 ⇄ utf8mb4
                                        DB/テーブル = utf8mb4 / utf8mb4_general_ci（保存は UTF-8）
                                                            ▲
                                        ホスト側スクリプト（create-account 等）= utf8mb4 接続

ログ: rAthena stdout (CP932) ─ stdbuf -oL iconv CP932→UTF-8 ─▶ Docker awslogs ─▶ CloudWatch (UTF-8)
      MariaDB / Docker / systemd / cloud-init = UTF-8
```

| レイヤ | 文字コード | 設定箇所 | 補足 |
|---|---|---|---|
| リポジトリ（翻訳ソース） | UTF-8 | `app/rathena/overlay-utf8/` | `scripts/check-overlay.sh` で BOM なし・CP932 変換可・LF を事前検査 |
| rAthena 実行ファイル群（npc / conf / db） | CP932 | Dockerfile で iconv | rAthena 本体の英語ファイルは ASCII なので影響なし |
| サーバ ⇄ クライアント | CP932 | クライアント `langtype 2` | rAthena は素通し |
| rAthena ⇄ MariaDB | 接続 cp932 / 保存 utf8mb4 | `inter_conf.txt`: `default_codepage` / `login_codepage` / `ipban_codepage` / `log_codepage` = `cp932`。MariaDB: `--character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci` | エスケープ処理もセッショントラッキングにより cp932 で動くことを `tests/cp932_roundtrip.c` で実測。**rAthena ソースは無改変** |
| DB 照合順序 | `utf8mb4_general_ci` | 同上 | ASCII の大文字小文字を同一視（rAthena 既定の「大文字小文字違いの同名不可」に整合）しつつ、ひらがな/カタカナ/全角半角は区別する。`utf8mb4_unicode_ci` / `uca1400_ai_ci` は「ぽりん」と「ポリン」を同一視するため不採用 |
| ホスト運用スクリプト | utf8mb4 | `mariadb --default-character-set=utf8mb4` | UTF-8 で SQL を送る |
| コンソールログ | CP932 → UTF-8 | `entrypoint.sh`（プロセス置換で変換。シグナルはサーバ本体に直接届く） | CloudWatch / `docker compose logs` で日本語が読める |

#### 10.3.1 パーサ制約（2026-09-23 判明）

rAthena `parse_variable()` の添字走査は文字列も 2 バイト文字も見ない生バイト走査のため、添字式 `var[...]` 内の文字列に CP932 で 2 バイト目が `[`/`]` になる文字（ー ゼ ゾ ‐ ほか 104 字）があると map-server が起動時に SIGSEGV で落ちる（再現不定）。ソースは無改変のまま、翻訳側で回避する（`docs/JP_TRANSLATION_RULES.md`、`tools/jp_structure_check.py` 検査 1c）。

### 10.4 サーバ設定の追加

| ファイル | 設定 | 意図 |
|---|---|---|
| `conf/import/inter_conf.txt.tmpl` | `default_codepage: cp932` ほか 3 キー | 接続文字コード |
| `conf/import/char_conf.txt.tmpl` | `char_name_option: 2`、`char_name_letters: !"#$%&'()*+,/:;<=>?` | 禁止リスト方式で日本語名を許可。禁止文字は CP932 の 2 バイト目（0x40-0x7E, 0x80-0xFC）と衝突しない 0x20-0x3F の記号のみ。`-` `.` 数字は許可。空白は設定ファイルの行頭トリムの都合で禁止にできない |
| `conf/import/battle_conf.txt` | `override_mob_names: 2` | Mob 名を `JapaneseName` に |
| `db/import/mob_db.yml`（overlay） | `Id` + `JapaneseName` | 初期セット。YAML はシングルクォートで CP932 安全 |
| `npc/scripts_custom.conf`（overlay） | `delnpc:` / `npc:` | 上流無改変で差し替え |
| `conf/msg_conf/import/map_msg_eng_conf.txt`（overlay） | 214 件 | 書式指定子（`%s` `%d` `%.*s` 等）の並びは原文と一致させる（位置指定子非対応） |
| `conf/motd.txt`（overlay） | 日本語 MOTD | — |

### 10.5 翻訳データの出所とライセンス

- **本プロジェクトの翻訳は全て独自訳**（rAthena 同梱の英語 NPC スクリプト / msg_conf を原文として日本語化）。rAthena は **GPL-3.0** なので翻訳版スクリプトも同ライセンスの派生物として扱う（ファイル冒頭に上流ヘッダを保持）。翻訳時のルール: 文字列リテラルのみ変更・構造不変（文字列を潰した diff が原本と一致することを機械検証）、`select` の項目数維持、日本語直後の `\` エスケープ禁止、CP932 に無い文字（U+301C 等）禁止。
- **Mob のカタカナ名**は独自転写だが、短い固有名詞ゆえ多くは jRO 公式表記と一致する。問題視する場合は `db/import/mob_db.yml` 1 ファイルの削除で英語に戻る（要判断）。
- **既存プロジェクトの調査結果（採用せず）**: Auriga（GPL-2.0、CP932、活発だが Auriga 独自形式で rAthena 非互換。item/mob 名は jRO 訳語由来の疑い）、jAthena（2012 年で停止）、rathena-intl（抽出の仕組みのみ、日本語データなし）、RATHENA 日本語化 Wiki（参照先リポジトリ消滅）、ROenglishRE（英語、ライセンス表記なし）、Divine-Pride（jRO 訳語、サイトが Gravity 帰属を明記）。**rAthena 向けにライセンスが明確な日本語 NPC 翻訳は見つからなかった。** jRO 公式テキストの転載は行わない。
- 調査で rathena.org フォーラムは取得不可（Cloudflare）だったため、コミュニティ投稿は根拠に使っていない。

### 10.6 クライアント側の要件（CLIENT_HANDOFF.md に転記する内容）

- クライアント: kRO **2021-11-03 RagexeRE**（rAthena PACKETVER 20211103）。jRO クライアントは不可。
- `clientinfo.xml`: `<servicetype>japan</servicetype>` と `<langtype>2</langtype>`（後者が有効）。`<address>` は EIP、`<port>6900`、`<version>55</version>`、`<langtype>` 以外は rAthena 標準例のとおり。
- WARP パッチ: **必要** = Disable 1rag1/1sak1 type parameters、Read Data Folder First または Enable Multiple GRFs、Always load Korea ExternalSettings lua file（langtype≠0 では `service_korea` しか無いため必要な可能性が高い）、Always Call SelectKoreaClientInfo()、Disable filename check（exe 名変更時）、Customize Font name（MS ゴシック / メイリオ等）。**不要** = Always read msgstringtable.txt・Use plain text descriptions（langtype≠0 では既定動作）、Disable Packet Encryption（2018-03-07 以降不要）。**最初は当てない** = Use Ascii on All LangTypes（マルチバイト判定を潰すため、日本語チャットの BackSpace 等に副作用の疑い。要検証）。
- クライアントが用意する日本語データ（CP932）: `data/msgstringtable.txt`、`data/mapnametable.txt`、`data/questid2display.txt`、`data/cardprefixnametable.txt`、`data/luafiles514/lua files/datainfo/*`（itemInfo）、`data/luafiles514/lua files/skillinfoz/*`、`UI\` 画像。jRO 公式データの流用は権利確認が必要。
- 可否整理: 日本語**表示** = langtype 2 + フォントで可。日本語**チャット** = サーバ側は透過で可、クライアント IME は要実機検証。日本語**キャラ名 / ギルド名 / パーティ名** = サーバ側は許可済み（全角 11 文字、最小 2 文字）、クライアント作成 UI での入力可否は要検証。
- 文字化けの切り分け: (1) `scripts/list-accounts.sh` や utf8mb4 接続の SELECT で DB の値が正しい日本語か → 正しければサーバ〜DB は正常。(2) CloudWatch の map-server ログで NPC 名が読めるか → 読めれば iconv 経路は正常。(3) クライアント `langtype` が 2 か、フォントが日本語対応か。(4) クライアント data ファイルが CP932 か（UTF-8 なら化ける）。(5) `?` に化ける → CP932 に無い文字（変換不能）。

### 10.7 日本語化の完成条件 → 確認方法

| # | 条件 | 確認方法 |
|---|---|---|
| J1 | 日本語文字列を MariaDB へ正常保存できる | cp932 接続で INSERT → utf8mb4 接続で SELECT して一致（`app/rathena/tests/cp932_roundtrip.c`、`ソ表能` の 0x5C 文字を含む）。**2026-09-23 ローカルで PASS 確認済み** |
| J2 | Server Log で日本語が化けない | map-server 起動ログの NPC 名（例: サポート職員）を CloudWatch / `docker compose logs` で確認 |
| J3 | 日本語 NPC script をロードできる | map-server ログに `script error` / `npc_parse` エラーが無いこと（`status.sh` がカウント表示） |
| J4 | 日本語 NPC メッセージを送信できる構成 | 実行ファイルが CP932 であること（`iconv` 変換ステップの成功 + `file` で確認）。最終確認はクライアント接続後 |
| J5 | 日本語 broadcast / announce | サーバは透過。`@broadcast` の動作はクライアント接続後に確認 |
| J6 | 日本語チャット仕様確認済み | §10.1 / §10.6 に記載 |
| J7 | Character / Guild / Party 名の日本語可否確認済み | §10.4（サーバ側許可）+ CLIENT_HANDOFF に制約記載 |
| J8 | クライアント側要件を CLIENT_HANDOFF.md に記載 | 作成時に確認 |
| J9 | サーバ / クライアントの責務を明文化 | §10.2 |
| J10 | 翻訳データの出所とライセンスを明記 | §10.5 |

### 10.8 第 2 フェーズで確定した方式（2026-09-24）

初期構築時の対象（§10.2 の初期セット）に加え、通常プレイ導線に沿って翻訳対象を拡張した第 2 フェーズ（Phase A/B/C）で、以下の方式を確定した。現在の対応ファイル数・件数・NPC 数などの数値は `docs/SPEC.md` を参照する（本節では方式のみ記す。経緯は `docs/CHANGELOG.md`、進捗は `docs/JP_NPC_PLAN.md`）。

- **頭上表示名（`日本語#suffix::旧フル名` 方式）**: rAthena は NPC を exname（`::` 以降のユニーク名）のみで参照する（`src/map/npc.cpp` `npc_parsename`/`npcname_db`）。そこで NPC ヘッダの表示名部分だけを日本語に書き換え、`::` 以降の exname は変更しない方式に統一した。これにより `doevent`/`donpcevent`/`enablenpc`/`disablenpc` 等、exname を経由する外部参照を一切壊さずに頭上表示だけ日本語化できる。対応表は `docs/jp-npc-names.tsv`（Source of Truth）、適用・検査ツールは `tools/jp_npc_names.py`（inventory/apply/check）。ヘッダは可視/不可視・`::` の有無で分類し（A=`::`あり/B=`::`追加/C=`strnpcinfo(0|1)` 依存で要判断/D=不可視・warp・shop は対象外）、C 分類（モンスター討伐時の `strnpcinfo(1)` 文字列比較などに使われる NPC 名）は日本語化すると比較処理が壊れるため英語のまま維持する（例: Merchant of Manuk / Merchant of Splendide）。
- **英語残りの機械監査**: `tools/jp_english_audit.py` で翻訳対象ファイル中に残る英語文字列を監査する。アイテム名・スキル ID 文字列・アナグラム等の言語依存パズル・Lorem ipsum のプレースホルダー・waitingroom のイベント名など、意図的に英語のまま残す箇所は `docs/jp-english-allowlist.tsv` に登録して監査対象から除外する。
- **`Global_Functions.txt` 追加のみ方式**: `npc/other/Global_Functions.txt` は上流を `delnpc` せず、翻訳版を MANIFEST の「追加のみ」エントリとして末尾に読み込ませる方式にした。同ファイル内の `F_getpositionname()` 等は `callfunc`（実行時解決）ではなく直接呼び出し構文で他 NPC から参照されており、パーサはパース時にその関数定義の存在を要求する。上流を先に `delnpc` で外すと未定義関数によるスクリプトエラーになるため、上流を残したまま翻訳版を後読みさせて同名関数を上書き（`npc_parse_function: Overwriting user function`）させ、パース時の解決を保ったまま実行時の返り値だけ日本語化した。
- **棚卸し**: 通常プレイ導線（修練場→プロンテラ→…→ジュノー、転職導線、日常 NPC）で未翻訳のまま残っているファイルの洗い出しは `docs/JP_COVERAGE_PHASE2.md` に記録している。
