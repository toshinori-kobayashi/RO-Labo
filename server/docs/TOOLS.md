# ツール・スクリプト一覧

本書のコマンドは `server/` ディレクトリを起点に実行する。

`scripts/`（Mac 側）、`app/scripts/`（EC2 側）、`tools/`（翻訳・検証用、Mac 側）に置かれている全スクリプトのリファレンスです。運用の流れ（いつ何を使うか）は `docs/OPERATIONS.md` を参照してください。本書は各スクリプトの目的・引数・入出力・注意点を単体で引けるようにまとめたものです。

記載内容はすべて各スクリプトのヘッダコメントと `--help`（`-h`）の出力に基づいています。挙動を確認したい場合は本書より先に `<script> --help` を実行してください。

## 共通の前提

- Mac 側スクリプト（`scripts/`）は AWS SSO プロファイル `sandbox-power` を前提にしています（`aws sso login --profile sandbox-power`）。
- EC2 へは SSH を使わず、**SSM（Session Manager / Run Command）経由のみ**です。`scripts/` の多くは `scripts/lib/common.sh` の `ssm_run` を使って `app/scripts/` の同名スクリプトを EC2 上で実行する「薄いラッパ」です。
- `app/scripts/` は EC2 上・`root` 実行が前提です（SSM Run Command は root として実行されるため、SSM 経由の呼び出しで `sudo` は不要）。対話シェル（`scripts/ssm-shell.sh` で入った場合）から直接叩くときは `sudo -i` してから実行します。
- `tools/` は Mac のリポジトリ直下で実行する Python 製の翻訳・検証ツール群です（標準ライブラリのみ、追加パッケージ不要）。

---

## 1. `scripts/`（Mac 側、SSM 経由）

| スクリプト | 目的 | EC2 側の対応スクリプト |
|---|---|---|
| `verify.sh` | ポート到達性 + リモート `status.sh` をまとめて確認 | `app/scripts/status.sh` |
| `status.sh` | EC2 上の `status.sh` を SSM 経由で実行 | `app/scripts/status.sh` |
| `logs.sh` | CloudWatch Logs からコンテナログを取得 | （EC2 に入らない） |
| `ssm-shell.sh` | SSM Session Manager で対話シェルに入る | — |
| `create-account.sh` | アカウント作成 | `app/scripts/create-account.sh` |
| `set-password.sh` | 既存アカウントのパスワード変更 | `app/scripts/set-password.sh` |
| `set-birthdate.sh` | 既存アカウントの生年月日設定 | `app/scripts/set-birthdate.sh` |
| `list-accounts.sh` | アカウント一覧表示 | `app/scripts/list-accounts.sh` |
| `backup-db.sh` | DB ダンプを即時実行 | `app/scripts/backup-db.sh` |
| `check-overlay.sh` | 日本語オーバーレイの事前検査（BOM/CP932/LF） | — |
| `check-jp-structure.sh` | NPC 翻訳ファイルの構造検証（薄いラッパ） | `tools/jp_structure_check.py` を呼ぶ |
| `local-smoke.sh` | ローカル（colima）でのフレッシュ起動スモークテスト | — |
| `lib/common.sh` | 共通関数（内部ライブラリ、直接実行しない） | — |

### `scripts/verify.sh`

- **目的**: 外部からのポート到達性を確認し、続けて EC2 上の `status.sh` を実行する。日常確認の入口。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  scripts/verify.sh                 # terraform output の public_ip を対象にする
  scripts/verify.sh --ip 1.2.3.4    # IP を直接指定
  scripts/verify.sh --ports-only    # リモートの status.sh を実行しない
  ```
- **入力と出力**: 入力は `terraform output`（`RO_PUBLIC_IP` で上書き可）。出力はポート 6900/6121/5121（open 期待）と 22/3306（closed 期待）の判定表、続けてリモート `status.sh` の内容。
- **注意点**: `nc` が必要（macOS 標準搭載）。判定 NG または `status.sh` 側が失敗すると終了コード非 0。

### `scripts/status.sh`

- **目的**: EC2 上の `app/scripts/status.sh` を SSM 経由で実行する。
- **実行場所**: Mac。
- **使い方**: `scripts/status.sh [--tail N]`（`--tail` は EC2 側にそのまま渡る。既定 2000 行）。
- **入力と出力**: 出力は `docker compose ps`、各サービスの起動ログ要点、NPC パースエラー件数、systemd の状態（EC2 側の項目は後述）。
- **注意点**: SSM `get-command-invocation` の出力は 24000 文字で打ち切られるため、長いログは `scripts/logs.sh` を使うこと。

### `scripts/logs.sh`

- **目的**: CloudWatch Logs からコンテナのログを取得する（EC2 に入らない）。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  scripts/logs.sh                        # 全ストリームを直近 10 分ぶん
  scripts/logs.sh map-server             # map-server のみ
  scripts/logs.sh map-server --since 1h  # 期間を指定
  scripts/logs.sh login-server --follow  # 追尾（-f も可）
  ```
  `service` は `login-server | char-server | map-server | mariadb`。
- **入力と出力**: `terraform output` からロググループ名を取得（`RO_LOG_GROUP` で上書き可）。出力は `aws logs tail` の結果。
- **注意点**: `aws` CLI が必要。`--since`/`--follow` 以外の不明な引数はエラーになる。

### `scripts/ssm-shell.sh`

- **目的**: SSM Session Manager で EC2 の対話シェルに入る。
- **実行場所**: Mac。
- **使い方**: `scripts/ssm-shell.sh`。入った後の定番操作は `sudo -i` → `cd /opt/ro-server && docker compose ps`。
- **前提**: `session-manager-plugin`（`brew install --cask session-manager-plugin`）。
- **注意点**: `terraform output` からインスタンス ID を取得する（`RO_INSTANCE_ID` で上書き可）。

### `scripts/create-account.sh`

- **目的**: rAthena のアカウントを SSM 経由で作成する（`app/scripts/create-account.sh` のラッパ）。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  scripts/create-account.sh <userid> <M|F> [group_id]
  RO_PASSWORD='...' scripts/create-account.sh <userid> <M|F> [group_id]
  ```
  `group_id` 既定は 0。99 = GM（Admin）。
- **入力と出力**: `RO_PASSWORD` 未指定なら EC2 側で英数 12 桁を生成し、標準出力に 1 回だけ表示される。
- **注意点**: `RO_PASSWORD` を指定した場合、値は SSM の実行コマンド（`send-command` の Parameters）に残る。残したくない場合は未指定で作成し、出力された値を使うこと。

### `scripts/set-password.sh`

- **目的**: 既存アカウントのパスワードを SSM 経由で変更する。
- **実行場所**: Mac。
- **使い方**: `RO_PASSWORD='...' scripts/set-password.sh <userid>`（`RO_PASSWORD` 必須。未指定だとエラーで終了する）。
- **注意点**: `RO_PASSWORD` の値は SSM Run Command の実行パラメータに残る（SSM コンソール等から参照可能）。残したくない場合は `scripts/ssm-shell.sh` で入り `sudo /srv/ro-server/app/scripts/set-password.sh <userid>` を対話実行する（無エコー入力・履歴に残らない）。

### `scripts/set-birthdate.sh`

- **目的**: 既存アカウントの生年月日（キャラクター削除の確認コード）を SSM 経由で設定する。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  scripts/set-birthdate.sh <userid> [YYYY-MM-DD]       # 省略時は 2000-01-01
  scripts/set-birthdate.sh --all-missing [YYYY-MM-DD]  # 生年月日が NULL の全アカウントに設定
  ```
- **注意点**: クライアントの削除確認ダイアログには `YYYYMMDD`（例 `20000101`）を入力する。詳細は `docs/OPERATIONS.md`「アカウント運用」。

### `scripts/list-accounts.sh`

- **目的**: `login` テーブルのアカウント一覧を SSM 経由で表示する。
- **実行場所**: Mac。
- **使い方**: `scripts/list-accounts.sh`（引数なし）。
- **出力**: account_id / userid / sex / group_id / logincount / lastlogin / last_ip。

### `scripts/backup-db.sh`

- **目的**: EC2 上で MariaDB のバックアップを即時実行する。
- **実行場所**: Mac。
- **使い方**: `scripts/backup-db.sh`（引数なし）。
- **出力**: ダンプ実行後 `/srv/ro-server/backups` の `ls -lh` 結果。
- **注意点**: 定期バックアップは systemd `ro-server-backup.timer`（毎日 04:00 JST）が別途行う。このスクリプトは任意タイミングの即時実行用。

### `scripts/check-overlay.sh`

- **目的**: `app/rathena/overlay-utf8/` がビルド時に CP932 へ変換できる状態かを Docker ビルド前に手元で確認する。
- **実行場所**: Mac（Linux でも動作）。
- **使い方**:
  ```sh
  scripts/check-overlay.sh            # app/rathena/overlay-utf8 を検査
  scripts/check-overlay.sh <dir>      # 任意のディレクトリを検査
  ```
- **検査項目**: (a) UTF-8 BOM が無いこと、(b) `iconv -f UTF-8 -t CP932` が成功すること、(c) 改行が LF（CR を含まない）であること。加えて U+301C（波ダッシュ）が無いことも見る（全角チルダ U+FF5E に統一する方針。glibc の iconv は U+301C を通してしまうが macOS の iconv は弾くため、環境差でビルド結果が変わらないよう禁止にしている）。
- **出力**: ファイルごとに OK/NG とサイズの一覧。NG の場合、CP932 変換不可なら該当行番号も表示する。
- **注意点**: 失敗があれば終了コード 1（ビルド前に必ず解消すること）。`scripts/check-jp-structure.sh` とは検査対象が異なる（こちらはエンコーディングのみ）。両方 PASS を `apply` の前提にする。

### `scripts/check-jp-structure.sh`

- **目的**: NPC 翻訳ファイルの構造検証（`tools/jp_structure_check.py` の薄いラッパ）。翻訳版が上流 rAthena に対して「文字列リテラルの中身以外は同一」であることを機械判定する。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  scripts/check-jp-structure.sh                        # MANIFEST.tsv 全件
  scripts/check-jp-structure.sh --report /tmp/jp.txt   # 結果をファイルにも保存
  scripts/check-jp-structure.sh \
      --file app/rathena/overlay-utf8/npc/custom/jp/cities/prontera.txt \
      --upstream npc/cities/prontera.txt               # 単体検証
  ```
  引数はそのまま `tools/jp_structure_check.py` に渡る（`--upstream-root` / `--commit` / `--strict-external-refs` など。詳細は本書「3. `tools/`」の `jp_structure_check.py` を参照）。
- **注意点**: FAIL があれば終了コード 1。`python3` が必須（無ければエラー終了）。

### `scripts/local-smoke.sh`

- **目的**: ローカル（Mac / colima）で `app/` をまっさらから起動し、map-server が NPC / マップを読み切れたかをログから機械判定する。NPC 翻訳ファイルを追加したあと、EC2 へ `apply` する前に必ず通すこと。
- **実行場所**: Mac（colima または Docker Desktop が起動済みであること）。
- **使い方**:
  ```sh
  scripts/local-smoke.sh
  scripts/local-smoke.sh --expect-npcs 13043 --report /tmp/smoke.txt
  ```
  オプション:
  | オプション | 内容 |
  |---|---|
  | `--expect-npcs N` | NPC 総数が N でなければ FAIL（上流差し替えは 1:1 なので総数は変わらない。変わるのは追加のみの独自 NPC を足したときだけ。現行値は 13043） |
  | `--report PATH` | 画面と同じ内容を UTF-8 でファイルへ保存 |
  | `--timeout SEC` | map-server が healthy になるまでの待ち時間（既定 360 秒） |
  | `--keep` | 終了時に `down` しない（ログを追加調査したいとき） |
  | `--no-build` | イメージを再ビルドしない |
- **処理内容**: `app/.env` が無ければ `.env.local.example` からコピー → 前回の残骸を `down` → `./.local/`（ローカル DB データ）を削除して初期化 → `docker compose -f docker-compose.yml -f docker-compose.local.yml up -d [--build]` → map-server が `healthy` になるまで待機 → ログから NPC 総数・エラー行・警告行を判定。
- **判定**: `[Error]` / `script error` / `npc_parse` が 1 行でもあれば FAIL（`[Info]` 行、例えば `npc_parse_function: Overwriting user function` は Global_Functions の正常な上書きなので数えない）。`--expect-npcs` 指定時は NPC 総数不一致も FAIL。map-server がタイムアウト内に healthy にならなければ FAIL。
- **注意点**: `./.local/` を削除できない場合（コンテナが root で作成したファイル）は `alpine` コンテナ経由で強制削除する。起動失敗時は overlay-utf8 の CP932 変換エラーを自動で抜粋表示する。

### `scripts/lib/common.sh`（内部ライブラリ）

直接実行するスクリプトではなく、`scripts/` 配下の各スクリプトが `source` して使う共通関数集です。

- `AWS_PROFILE`（既定 `sandbox-power`）、`REGION`（既定 `ap-northeast-1`）を環境変数で上書き可能。
- `instance_id` / `public_ip` / `log_group`: `terraform output` から取得（`RO_INSTANCE_ID` / `RO_PUBLIC_IP` / `RO_LOG_GROUP` で直接指定して `terraform` 呼び出しを省略できる）。
- `ssm_run "<shell command>" ["<comment>"]`: `AWS-RunShellScript` で EC2 上のコマンドを実行し、標準出力／標準エラーを表示する（SSM Agent は root で実行するので `sudo` は不要）。失敗時は非 0 で終了する。`get-command-invocation` の出力は 24000 文字で打ち切られる点に注意（長いログは `scripts/logs.sh` を使う）。
- `shq`: シングルクォートで囲むエスケープ関数（SSM 経由でリモートコマンドに引数を渡すときに使う）。
- `require_tools` / `die` / `info`: 前提コマンドの存在確認、エラー終了、進捗表示の補助関数。

---

## 2. `app/scripts/`（EC2 側、SSM 経由 / systemd から呼ばれる）

配布物 `app/` の一部として `/srv/ro-server/app/scripts/` に配置されます。ほとんどは `scripts/`（Mac 側）の同名スクリプトから SSM 経由で呼ばれますが、`deploy.sh` / `init-env.sh` / `update-public-ip.sh` の 3 本は Mac 側に対応スクリプトが無く、デプロイ処理・systemd から直接呼ばれます。

| スクリプト | 目的 | 呼び出し元 |
|---|---|---|
| `create-account.sh` | アカウント作成（DB へ INSERT） | `scripts/create-account.sh` |
| `set-password.sh` | パスワード変更（DB へ UPDATE） | `scripts/set-password.sh` または対話実行 |
| `set-birthdate.sh` | 生年月日設定（DB へ UPDATE） | `scripts/set-birthdate.sh` |
| `list-accounts.sh` | アカウント一覧（DB へ SELECT） | `scripts/list-accounts.sh` |
| `backup-db.sh` | DB ダンプ取得 | `scripts/backup-db.sh` / `ro-server-backup.timer` |
| `restore-db.sh` | DB ダンプからのリストア | 対話実行のみ |
| `status.sh` | コンテナ状態・ログ要点の表示 | `scripts/status.sh` / `scripts/verify.sh` / `deploy.sh` 末尾 |
| `deploy.sh` | デプロイ本体（`.env` 同期・ビルド・再起動） | SSM Association |
| `init-env.sh` | `.env` の冪等な用意（秘密情報生成） | `deploy.sh` |
| `update-public-ip.sh` | IMDSv2 から Public IP を取得して `.env` に反映 | `deploy.sh` / systemd `ExecStartPre` |

### `app/scripts/create-account.sh`

- **目的**: rAthena のアカウントを `login` テーブルへ作成する。
- **実行場所**: EC2 上・root。
- **使い方**:
  ```sh
  create-account.sh <userid> <M|F> [group_id]
  RO_PASSWORD='...' create-account.sh <userid> <M|F> [group_id]
  ```
  - `userid`: `^[A-Za-z0-9_]{4,23}$`（`login.userid` は varchar(23)）。
  - `group_id`: 既定 0。GM は 99（`conf/groups.yml` Id 99 = Admin / `all_commands` / `LogCommands`）。0〜99 の整数以外はエラー。
  - `RO_PASSWORD` 未設定なら英数 12 桁を生成し、標準出力に **1 回だけ**表示する（`use_MD5_passwords: no` のため `login.user_pass` には平文で入る）。パスワードは `^[A-Za-z0-9_@#%+=.-]{4,23}$` を満たす必要がある。
  - `RO_BIRTHDATE='YYYY-MM-DD'` で生年月日を指定できる（既定 `2000-01-01`）。キャラクター削除の確認コード（クライアントで `YYYYMMDD` を入力、サーバには下 6 桁 `YYMMDD` が届く）。NULL のままだと PACKETVER 20211103 クライアントからは削除不能なため、必ず値を入れる。
- **入力と出力**: 標準出力に作成結果（account_id / userid / sex / group_id / password（生成時のみ）/ birthdate）と、作成後の行を `--table` 形式で表示。
- **注意点**: 同一 `userid` が既に存在する場合はエラーで終了する。パスワード・SQL リテラルは適切にエスケープされる。DB 接続は `--default-character-set=utf8mb4`（rAthena 本体の接続は cp932 だが、テーブル自体は utf8mb4 のため）。

### `app/scripts/set-password.sh`

- **目的**: 既存アカウントのパスワードを変更する。
- **実行場所**: EC2 上・root。
- **使い方**:
  ```sh
  set-password.sh <userid>                    # 対話: 無エコーで 2 回入力
  RO_PASSWORD='...' set-password.sh <userid>   # 非対話
  ```
- **注意点**: パスワードは `^[A-Za-z0-9_@#%+=.-]{4,23}$`（`login.user_pass` は varchar(32)、`use_MD5_passwords: no` のため平文保存）。値は一切表示・記録しない。非対話実行（標準入力が tty でない）で `RO_PASSWORD` 未指定だとエラーになる。対象 `userid` が存在しない場合もエラー。

### `app/scripts/set-birthdate.sh`

- **目的**: 既存アカウントの生年月日（キャラクター削除の確認コード）を設定する。
- **実行場所**: EC2 上・root。
- **使い方**:
  ```sh
  set-birthdate.sh <userid> [YYYY-MM-DD]        # 省略時は 2000-01-01
  set-birthdate.sh --all-missing [YYYY-MM-DD]   # 生年月日が NULL の全アカウントにまとめて設定（account_id=1 は除外）
  ```
- **注意点**: PACKETVER 20211103 のクライアントは 0x0829（生年月日 YYMMDD）でしか削除を確定できず、`login.birthdate` が NULL のアカウントはキャラクターを削除できない。変更は**次回 char-server ログインから有効**（既にログイン中のセッションには反映されない）。パスワード等の秘密情報は扱わない。

### `app/scripts/list-accounts.sh`

- **目的**: `login` テーブルのアカウント一覧を表示する。
- **実行場所**: EC2 上・root。
- **使い方**: `list-accounts.sh`（引数なし）。
- **出力**: account_id / userid / sex / group_id / logincount / lastlogin / last_ip を `--table` 形式で表示。
- **注意点**: `account_id=1` は inter-server 用のシステムアカウント（`sex='S'`）。

### `app/scripts/backup-db.sh`

- **目的**: MariaDB のダンプを `/srv/ro-server/backups` に取る。
- **実行場所**: EC2 上・root（systemd `ro-server-backup.timer` から毎日 04:00 JST に呼ばれる）。
- **使い方**: `backup-db.sh [--help]`。環境変数 `APP_DIR`（既定 `/srv/ro-server/app`）、`BACKUP_DIR`（既定 `/srv/ro-server/backups`）、`RETENTION_DAYS`（既定 7）で上書き可能。
- **入力と出力**: `mariadb-dump --single-transaction --quick --routines --events` を `--default-character-set=utf8mb4` で実行し、`ragnarok-<YYYYmmdd-HHMMSS>.sql.gz` として保存。完了後、保持日数を超えたダンプ（`ragnarok-*.sql.gz`、`mtime` 基準）を削除する。
- **注意点**: 展開後のサイズが 1KB 未満、または `CREATE TABLE` を含まない場合はダンプ失敗として扱い、ファイルを残さない（不完全なバックアップを検知するため）。認証情報はホスト側の argv に出さず、コンテナ内の環境変数をコンテナ内のシェルで展開する方式。

### `app/scripts/restore-db.sh`

- **目的**: バックアップから MariaDB をリストアする。
- **実行場所**: EC2 上・root（対話実行のみ。自動実行される経路は無い）。
- **使い方**:
  ```sh
  restore-db.sh /srv/ro-server/backups/ragnarok-YYYYmmdd-HHMMSS.sql.gz
  FORCE=1 restore-db.sh <file>   # 確認プロンプトを省略（非対話実行用）
  ```
- **処理内容**: login/char/map の 3 サービスを `docker compose stop` → `zcat <file> | mariadb --default-character-set=utf8mb4 -u root` でリストア → `docker compose up -d` → `status.sh --tail 200` を表示。
- **注意点**: **現在の DB の内容は失われる**。`FORCE=1` 未指定時は `yes` の入力を要求する。リストアに失敗した場合、サービスは停止したまま終了する（再起動は手動で行う）。

### `app/scripts/status.sh`

- **目的**: コンテナの状態と各サーバの起動ログの要点を表示する。
- **実行場所**: EC2 上・root。
- **使い方**: `status.sh [--tail N]`（既定 N=2000。`docker compose logs --tail` に渡す取得行数）。
- **出力構成**:
  - `docker compose ps`
  - login-server: `The login-server is` / `Connection of the char-server` / `Couldn't connect with uname=` / `[Error]` / `[SQL]` に一致する行（末尾 40 行）
  - char-server: `Connected to login-server` / `The char-server is` / `DB integrity check finished` / `Connection to Login Server lost` / `[Error]`
  - map-server: `Connect success!` / `Loading maps (using` / `Successfully loaded` / `Done loading` / `Successfully logged on to Char Server` / `Server is 'ready'` / `Connection to char-server failed` / `[Error]`（該当行の後続 6 行も含む）
  - **map-server NPC パース**: `script error` / `npc_parse` / `Unknown` の件数と該当行（末尾 20 行）。日本語版 NPC への差し替え結果、パース失敗が無いかをここで確認する。いずれも 0 件でなければ `docker compose logs map-server` を直接確認すること。
  - mariadb ログ末尾 50 行中 20 行
  - systemd: `ro-server.service` の active/enabled、`ro-server-backup.timer` の active/次回実行
- **注意点**: grep するパターンは rAthena の実ソース（`RATHENA_COMMIT` のコミット）の該当行に合わせてヘッダコメントに記載されている（`src/login/login.cpp:907` 等）。色コードは `stdout_with_ansisequence: no` のため出力時に除去済み。

### `app/scripts/deploy.sh`

- **目的**: EC2 上のデプロイ本体（root 実行・冪等）。
- **実行場所**: EC2 上・root（SSM Association から呼ばれる。呼び出し元は user-data 完了待ち → S3 から `app.zip` 取得 → `rsync -a --delete --exclude .env` で `/srv/ro-server/app` へ同期 → `chown -R ec2-user` → `deploy.sh` の順）。
- **使い方**: `deploy.sh`（通常デプロイ）、`SKIP_BUILD=1 deploy.sh`（設定変更のみ反映したいときにイメージビルドを飛ばす）。
- **処理内容**（7 ステップ）:
  1. ファイルのパーミッションを整える（zip 配布で実行ビットが落ちることがあるため `scripts/*.sh` / `rathena/entrypoint.sh` を 755 に、`rathena/sql-init/*` を 644 に。sql-init は実行ビットが無いことが MariaDB の initdb に source させる条件）
  2. `.env` の生成・同期（`init-env.sh` を呼ぶ）
  3. Public IP の取得（`update-public-ip.sh` を呼ぶ）
  4. `.env` の権限確認（600・所有者 ec2-user でなければ修正）
  5. systemd unit（`ro-server.service` / `ro-server-backup.service` / `ro-server-backup.timer`）の配置・`daemon-reload`・`enable`
  6. イメージのビルド（`SKIP_BUILD=1` でなければ `docker compose build --pull`。build args は `.env` から補間）
  7. `systemctl restart ro-server.service` と `ro-server-backup.timer` の起動、最後に `status.sh` を表示
- **出力**: SSM 側で `/var/log/ro-server-deploy.log` に tee される。
- **注意点**: root 以外で実行するとエラー。`$APP_DIR` が存在しないとエラー。

### `app/scripts/init-env.sh`

- **目的**: `/srv/ro-server/app/.env` を冪等に用意する。
- **実行場所**: EC2 上・root（`deploy.sh` から呼ばれる）。
- **使い方**: `init-env.sh [--help]`。環境変数 `APP_DIR`（既定 `/srv/ro-server/app`）、`ENV_OWNER`（既定 `ec2-user`）。
- **処理内容**: `.env` が無ければ新規作成、あれば `config.env` 由来のキーだけを同期（値を置換・無ければ追記）。`MARIADB_ROOT_PASSWORD` / `MARIADB_PASSWORD` / `INTERSERVER_USER`（`s_` + 英数 8 桁） / `INTERSERVER_PASSWORD` が未設定のときだけ `openssl rand` ベースの英数字で新規生成する。`PUBLIC_IP` のキーが無ければ空で用意する（値は `update-public-ip.sh` が入れる）。
- **注意点**: **`.env` を消して作り直すと DB のパスワードだけ新しくなり、既存の `/srv/ro-server/mariadb`（初期化済み）と食い違って起動しなくなる**。作り直す場合は DB も初期化するか、旧 `.env` から秘密情報を復元すること。生成した秘密情報の値は一切表示しない。`umask 077` で `.env` は常に 0600。

### `app/scripts/update-public-ip.sh`

- **目的**: IMDSv2 から Public IP を取得して `.env` の `PUBLIC_IP` を更新する。
- **実行場所**: EC2 上・root（`deploy.sh` および systemd `ro-server.service` の `ExecStartPre` から呼ばれる）。
- **使い方**: `update-public-ip.sh [--help]`（引数なし）。
- **処理内容**: IMDSv2 トークンを取得 → `public-ipv4` メタデータを取得 → `.env` の `PUBLIC_IP` を更新。値が変わらなければ何もしない。
- **注意点**: コンテナに IMDS を触らせないため、ホスト側（EC2 の OS）で取得して `.env` に書く設計。取得に失敗した場合は既存値を維持して警告のみで正常終了する。既存値も無ければ異常終了する（`.env` が無い場合も同様にエラー）。

---

## 3. `tools/`（翻訳・検証、Mac 側）

NPC 日本語化オーバーレイ（`app/rathena/overlay-utf8/`）の生成・検証・バックアップと、実パケットでの動作検証を行う Python / Shell ツール群です。翻訳ルールそのものは `docs/JP_TRANSLATION_RULES.md`、運用フローは `docs/OPERATIONS.md`「日本語化の運用手順」を参照してください。

| ツール | 目的 |
|---|---|
| `gen-jp-conf.py` | `MANIFEST.tsv` から `scripts_custom.conf` の JP ブロックを生成 |
| `jp_structure_check.py` | 翻訳版 NPC スクリプトの構造検証（文字列リテラル以外が上流と同一か） |
| `jp_english_audit.py` | 翻訳済みファイルに残る英語表示文字列の監査（読むだけ） |
| `jp_npc_names.py` | NPC 頭上表示名の棚卸し / 適用 / 検査（`inventory` / `apply` / `check`） |
| `jp-backup.sh` | 日本語化オーバーレイのバックアップ |
| `jp-restore.sh` | バックアップからの復元 |
| `jp_common.py` | 上記 Python ツールの共通部品（内部ライブラリ、直接実行しない） |
| `chardel_probe.py` | rAthena の実パケットでキャラ削除 / NPC 会話 / map 入場を検証する最小クライアント |

### `tools/gen-jp-conf.py`

- **目的**: `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv`（Source of Truth）から `app/rathena/overlay-utf8/npc/scripts_custom.conf` の JP ブロック（`// ---- BEGIN JP OVERLAY ... ----` 〜 `// ---- END JP OVERLAY ----`）を機械生成する。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  tools/gen-jp-conf.py                          # 生成して書き込む
  tools/gen-jp-conf.py --check                  # 生成せず差分の有無だけ返す（差分あり = 終了コード 1）
  tools/gen-jp-conf.py --upstream-root /path/to/rathena
  ```
  オプション: `--manifest`（MANIFEST.tsv のパス）、`--conf`（scripts_custom.conf のパス）、`--upstream-root`（既定は scratchpad → `~/.cache/rathena-<commit>`）、`--commit`（既定は `app/config.env` の `RATHENA_COMMIT`）。
- **生成前の検証**: (a) 翻訳版ファイルが overlay-utf8 に存在する、(b) 上流パスが上流 checkout に存在する、(c) 上流パスが Pre-RE のロード対象（`npc/pre-re/scripts_main.conf` を再帰展開した `npc:` 集合）に文字列として完全一致で含まれる（`delnpc` は文字列一致で効くため）、(d) 上流パス・翻訳版パスに重複が無い。さらに生成計画自体も (e) 同一上流パスの二重登録が無いこと、(f) `duplicate` 元より後ろに並んでいることを検証する。1 つでも失敗すれば生成せず非 0 で終了する。
- **入力と出力**: 入力は `MANIFEST.tsv`（上流パス TAB 翻訳版パス）。出力は `scripts_custom.conf` の JP ブロック（`delnpc:`/`npc:` の対、および duplicate 依存の再登録行）。
- **注意点**: JP ブロックは手で編集しない（次の生成で上書きされる）。差し替えを増やすときは `MANIFEST.tsv` に 1 行足してこのツールを実行する。`jp_structure_check.py` のトークナイザ／ヘッダ検出を内部で流用する。

### `tools/jp_structure_check.py`

- **目的**: 翻訳版 NPC スクリプトが上流と「文字列リテラル以外は同一」であることを検証する。簡易トークナイザで両者を読み、トークン列（文字列は `"STR"` プレースホルダ化、コメント除去、空白正規化）が完全一致するかを見た上で、文字列リテラルの対応関係（マップ名・イベント名・比較値・`select` の項目数・書式指定子など）を個別に検査する。
- **実行場所**: Mac（`scripts/check-jp-structure.sh` から薄くラップされて呼ばれることが多い）。
- **使い方**:
  ```sh
  tools/jp_structure_check.py                       # MANIFEST 全件
  tools/jp_structure_check.py --file app/... --upstream npc/cities/prontera.txt
  tools/jp_structure_check.py --report /tmp/jp-structure.txt
  ```
  オプション: `--manifest`、`--file`＋`--upstream`（単体検証）、`--upstream-root`、`--commit`、`--report`（結果を UTF-8 で保存）、`--strict-external-refs`（改名した表示名が他ファイルから `::` 付きでも引用されていたら FAIL にする）。
- **検査項目**（ファイルごとに PASS / FAIL / WARN）:
  1. エンコーディング: UTF-8 厳密・BOM なし・CR なし・CP932 変換可・禁止文字なし（U+301C 波ダッシュ・U+2212・半角カナ・U+FFFD・BMP 外）、非 ASCII 文字の直後の `\` も FAIL。
  1b. エスケープ: 文字列リテラル内の `\` の直後が非 ASCII、または rAthena が解釈できないエスケープ（`sv_unescape_c: empty escape sequence` の原因）を検出。
  1c. 添字走査: 添字式 `var[...]` 内の文字列に CP932 2 バイト目が `[`/`]` になる文字（「ー」「ゼ」「ゾ」「‐」等）が無いか（`parse_variable()` の生バイト走査がファイル末尾を越えて map-server が SIGSEGV になる原因）。上流にも同じものがある場合は除外。
  2. トークン構造: 上流と完全一致（不一致なら最初の相違位置を表示）。
  3. ヘッダ: 表示名は `日本語#suffix::旧フル名` の形でのみ変更可（exname・`#suffix`・座標・種別・sprite は不変。表示名は CP932 50 バイト以内）。
  4. 文字列リテラル: 同一必須の引数 / `::` を含むイベント参照 / 比較値の一意性 / `select` の項目数 / 書式指定子 / 色コード。
  5. 外部参照: exname が不変で、他ファイルからの参照が壊れないこと（旧表示名の文面上の引用は WARN）。
  5b. 表示名依存: 表示名を変えた NPC が `strnpcinfo(0|1)` を比較・キーに使っていないか（WARN）。
  6. 件数: `mes` / `select` / 文字列数（参考表示）。
- **注意点**: FAIL が 1 つでもあれば終了コード 1。`gen-jp-conf.py` と `jp_english_audit.py` はこのモジュールのトークナイザ等を import して再利用している。

### `tools/jp_english_audit.py`

- **目的**: 翻訳済み NPC スクリプトに残る英語表示文字列を機械的に洗い出す（読むだけ、ファイルは変更しない）。`jp_structure_check.py` が「構造」を見るのに対し、こちらは「プレイヤーに見える文字列が日本語になっているか」だけを見る。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  tools/jp_english_audit.py                             # MANIFEST 全件
  tools/jp_english_audit.py --file app/rathena/overlay-utf8/npc/custom/jp/...
  tools/jp_english_audit.py --out docs/jp-english-audit-20260924.tsv
  tools/jp_english_audit.py --strict                    # 許容リストを無視して全件
  ```
  オプション: `--manifest`、`--file`（単体監査）、`--allowlist`（既定 `docs/jp-english-allowlist.tsv`）、`--out`（候補一覧を TSV で保存）、`--strict`、`--quiet`（候補一覧を標準出力に出さない）、`--unused-allow`（一度もマッチしなかった許容リスト行を表示）。
- **対象にする文字列**: `mes` / `select` / `prompt` / `menu` の選択肢 / `next` の引数 / `dispbottom` / `message` の第 2 引数 / `announce` の第 1 引数 / `mapannounce` の第 2 引数 / `npctalk` / `unittalk` のメッセージ / `showscript` / `waitingroom` のタイトル。**対象にしないもの**: `callfunc`/`callsub` に渡す文字列、マップ名・イベント名・NPC 名などの識別子、比較値、コメント、ヘッダ行。
- **判定ロジック**: 色コード `^RRGGBB` と `%d`/`%s` 等を除去した後、(a) 英字 3 文字以上の単語が 2 語以上連続、または (b) 英字のみの単語が 8 文字以上、のどちらかに当たると「英語残り候補」。
- **許容リスト** `docs/jp-english-allowlist.tsv`（TAB 区切り 3 列 `<file><TAB><pattern><TAB><reason>`）: `file` は対象ファイル（空 または `*` で全ファイル、overlay 相対パス／ファイル名どちらにも glob で当たる）、`pattern` は正規表現（マッチ部分を判定前に除去=許容）、`reason` は許容理由（レポート用）。
- **注意点**: ファイルは一切変更しない（監査のみ）。意図的に英語のまま残す文字列（アイテム名・URL・暗号パズル等）は許容リストで管理する。

### `tools/jp_npc_names.py`

- **目的**: NPC の頭上表示名を `日本語#suffix::旧フル名` 形式で日本語化するための棚卸し／適用／検査。rAthena は `表示名::ユニーク名` のうち exname（`::` の後ろ）だけで NPC を参照するため、表示名だけを機械的に書き換える。
- **実行場所**: Mac。サブコマンド 3 つ。

  **`inventory`** — ヘッダを棚卸しして対応表 TSV を出力する。
  ```sh
  tools/jp_npc_names.py inventory --out docs/jp-npc-names.tsv
  ```
  オプション: `--out`（既定 `docs/jp-npc-names.tsv`）、`--manifest`、`--upstream-root`、`--commit`。出力 TSV の主な列: `file`/`line`（翻訳版ファイルとヘッダ行）、`kind`（script/duplicate/shop/warp/function）、`upstream_name`/`current_name`、`display`/`hidden`/`exname`（現在名の分解）、`visible`（頭上に名前が出るか）、`speaker_tags`/`first_tag`（本文の話者タグ）、`refs_exname`/`refs_display_text`（他ファイルからの参照件数と例）、`strnpcinfo_use`、`category`（A=`::`あり / B=`::`を足せば安全 / C=要個別判断 / D=対象外）、`proposed_jp`（自動提案）、`apply_jp`（**人間が確定した日本語。ここだけ編集する**）、`note`。

  **`apply`** — 対応表の `apply_jp` 列に従ってヘッダ行を書き換える。
  ```sh
  tools/jp_npc_names.py apply --map docs/jp-npc-names.tsv [--dry-run] [--only-file <path>]
  ```
  `--dry-run` は差分だけ表示して書き換えない。`--only-file` は特定ファイルだけ処理する。

  **`check`** — 対応表と現ファイルの整合を検査する。
  ```sh
  tools/jp_npc_names.py check --map docs/jp-npc-names.tsv
  ```
- **編集ルール**: 人間が編集するのは `apply_jp` 列だけで、**可視部分の日本語だけ**を書く（`#suffix` と `::exname` はツールが上流ヘッダから機械的に引き継ぐ）。空欄の行は変更されない。`::` `#` タブ・制御文字は使用不可、CP932 で表せない文字も不可、`#suffix` 込みの CP932 バイト長は 50 以内（`NPC_NAME_LENGTH`）。
- **注意点**: 対応表 `docs/jp-npc-names.tsv` が Source of Truth。手編集で対応表以外（NPC ファイル本体のヘッダ）を直接書き換えない。

### `tools/jp_common.py`（内部ライブラリ）

`gen-jp-conf.py` / `jp_structure_check.py` / `jp_english_audit.py` などが import する共通部品（標準ライブラリのみ）。直接実行しない。提供するもの: リポジトリ内の固定パス（overlay / MANIFEST / scripts_custom.conf）、`app/config.env` からの `RATHENA_COMMIT` 取得、`MANIFEST.tsv` のパース、上流 rAthena（固定コミット）のファイル取得（ローカル checkout もしくは GitHub raw を `~/.cache/rathena-<commit>/` にキャッシュ。環境変数 `RATHENA_UPSTREAM_ROOT` でも上書き可）、Pre-RE でロードされる `npc:` パス集合の算出。

### `tools/jp-backup.sh`

- **目的**: NPC 日本語化作業のバックアップ。翻訳バッチを始める前・大きな一括置換の前に実行する。
- **実行場所**: Mac。
- **使い方**: `tools/jp-backup.sh <label>`（例: `tools/jp-backup.sh before-batch-2`）。
- **保存先**: `backups/jp-translation/<label>-<YYYYmmdd-HHMMSS>/` に以下をコピーする。
  - `overlay-utf8/`: `app/rathena/overlay-utf8` 全体
  - `docs/JP_GLOSSARY.md`（あれば）
  - `tools/`: 検証・生成ツール一式
  - `scripts/check-jp-structure.sh` / `check-overlay.sh` / `local-smoke.sh`
  - `RESTORE.md`: 復元手順（自動生成）
  - `MANIFEST-snapshot.tsv`: その時点の `MANIFEST.tsv`
  - `sha256sums.txt`: バックアップ内全ファイルのハッシュ
- **注意点**: `label` に `/` や空白は使えない。復元は `tools/jp-restore.sh <backup-dir>`。

### `tools/jp-restore.sh`

- **目的**: `jp-backup.sh` が作ったバックアップから `app/rathena/overlay-utf8/` を丸ごと復元する。
- **実行場所**: Mac。
- **使い方**:
  ```sh
  tools/jp-restore.sh --dry-run <backup-dir>   # 差分ファイル一覧だけ表示
  tools/jp-restore.sh <backup-dir>             # 復元する
  ```
  `<backup-dir>` は `backups/jp-translation/<label>-<ts>`（相対でも絶対でも可）。
- **処理内容**: バックアップの `overlay-utf8/` と現状の差分（`diff -rq`）を表示。`--dry-run` でなければ、実行前に現状を `backups/jp-translation/pre-restore-<ts>/` へ自動退避（内部で `jp-backup.sh pre-restore` を呼ぶ）してから丸ごと置き換える。
- **注意点**: 復元後は `scripts/check-overlay.sh` / `scripts/check-jp-structure.sh` / `tools/gen-jp-conf.py --check` を実行して整合を確認すること（このスクリプト自身も最後に案内を表示する）。差分が無い場合は何もしない。

### `tools/chardel_probe.py`

- **目的**: rAthena の login → char → map の正規パケットを実際に送って、キャラクター削除・NPC 会話（修練場スキップ）・map 入場が正規経路で動くかを検証する最小クライアント（標準ライブラリのみ）。対象は Pre-Renewal（`--enable-prere`）/ PACKETVER 20211103 / パケット難読化キー 0（暗号化なし）。パケット番号・レイアウトは rAthena 本体ソース（本番と同一コミット `e985006`）から確認した値のみを使用している。
- **実行場所**: **EC2 内から `--host 127.0.0.1` で実行すること**（Mac から EIP 越しに実行すると、同一 char セッションの 3 回目の要求に対する応答が届かず失敗する事象を確認済み。サーバ側は EC2 内からの同じ手順で全段階成功している）。`scripts/ssm-shell.sh` で入って配置するか、SSM Run Command で base64 を分割転送する（`tools/` は `app/` の配布に含まれないため、EC2 へは別途転送が必要）。
- **使い方（主なオプション）**:
  ```
  --host HOST                login-server のホスト/IP（必須）
  --login-port LOGIN_PORT    login-server のポート（既定 6900）
  --user USER                アカウント名（login.userid、必須）
  --birthdate BIRTHDATE      login.birthdate を YYYYMMDD で指定（0x0829 に YYMMDD を載せる、必須）
  --name NAME                作成/削除の対象キャラクター名
  --slot SLOT                作成先スロット（省略時は空きスロット）
  --create                   --name のキャラクターを作成する
  --delete                   対象キャラクターを 0x0827 -> 0x0829 で削除する
  --cancel-reservation       削除予約を 0x082b で取り消して結果を表示する
  --enter-map                残っているキャラクター 1 体で map まで入って即 quit する
  --npc-skip MODE            修練場の NPC「冒険者支援員」に話しかけて一次職転職を検証する
                              MODE = acolyte | archer | mage | merchant | swordman | thief
                              / decline（7 番「まだ修練場を続ける」）/ cancel（確認で「いいえ」）
  --npc-skip-cancel-job JOB  --npc-skip cancel のときに 7 択で選ぶ職（既定 swordman）
  --keep                     削除を行わない（--delete を無効化）
  --timeout TIMEOUT          各 recv のタイムアウト秒（既定 10。RTT の大きい回線では増やす）
  --json PATH                結果を JSON で書き出す
  --verbose / -v             パケットトレースを stderr に出す
  ```
- **パスワード**: 環境変数 `RO_PROBE_PASSWORD` からのみ取得する（引数・ログ・JSON のいずれにも出力しない）。
- **入力と出力**: 標準出力に各ステップの結果（例: `HC_DELETE_CHAR3_RESERVED(0x0828): result=1 (予約成功)`）。`--json PATH` で機械可読な結果も残せる。
- **注意点**: `--verbose` はパケットの生バイトトレースを stderr に出すため、通常運用ではログに残さないこと。`--delete` はキャラクターを実際に削除する破壊的操作（検証専用アカウントで使うこと。`docs/OPERATIONS.md`「アカウント運用」の `deltest01` を参照）。
