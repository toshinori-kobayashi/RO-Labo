# 運用手順書（Runbook）

本書のコマンドは `server/` ディレクトリを起点に実行する。

rAthena Pre-Renewal 検証サーバの日常運用・変更作業・障害対応の手順です。構築手順や全体設計は `README.md` / `docs/DESIGN.md` を参照してください。各スクリプトの引数・入出力の詳細なリファレンスは `docs/TOOLS.md` を参照してください。本書は「次に何をやるか」を素早く引ける runbook として、手順寄りにまとめています。

前提: AWS SSO プロファイル `sandbox-power`、EC2 へは SSM 経由のみ（SSH 不可）。

## 日常確認

```sh
scripts/verify.sh
```

ポート到達性（6900/6121/5121 open、22/3306 closed）と、EC2 上の `status.sh`（`docker compose ps`、各サービスの起動ログ要点、NPC パースエラー件数、systemd の状態）をまとめて確認します。aws-nuke が毎日 05:00 JST に走るため（詳細は後述）、**その直後に 1 回実行しておくと異常の早期発見になります**。

個別に見たいときは以下を使い分けます（各スクリプトの詳細は `docs/TOOLS.md`）。

| 見たいもの | コマンド |
|---|---|
| ポート到達性だけ | `scripts/verify.sh --ports-only` |
| EC2 上のサービス状態・ログ要点 | `scripts/status.sh [--tail N]` |
| CloudWatch Logs（期間・追尾指定可） | `scripts/logs.sh [service] [--since 1h] [--follow]` |
| 対話シェルで直接調査 | `scripts/ssm-shell.sh` |

### healthy の見方

`status.sh` の `docker compose ps` 欄で各サービスが `healthy` になっていれば正常です。ヘルスチェックは `app/docker-compose.yml` で以下のとおり定義されています。

| サービス | 判定方法 | interval | start_period |
|---|---|---|---|
| mariadb | `healthcheck.sh --connect --innodb_initialized`（公式イメージ同梱） | 10s | 120s |
| login-server | `/dev/tcp/127.0.0.1/6900` への接続 | 10s | 30s |
| char-server | `/dev/tcp/127.0.0.1/6121` への接続 | 10s | 30s |
| map-server | `/dev/tcp/127.0.0.1/5121` への接続 | 10s | 180s（マップ/NPC 読み込みに時間がかかるため長め。retries も 30 回と多め） |

### CloudWatch の healthcheck ノイズの読み飛ばし

login/char/map の各コンテナは 10 秒ごとに `127.0.0.1` からの TCP 接続チェックを受けます。このため CloudWatch Logs（および `docker compose logs`）には **`Closed connection from 127.0.0.1` のような行が 10 秒間隔で継続的に出ます**。これはヘルスチェック自体のログであり異常ではありません。ログ調査（`scripts/logs.sh`）で流れを追うときは、このパターンをノイズとして読み飛ばしてください。実際の問題（`[Error]`、`script error`、`npc_parse`、`Connection to char-server failed` 等）は別の文言で出ます。

## アプリ更新（`app/` 配下の変更）の標準手順

1. `app/` 配下（`docker-compose.yml`、`config.env`、`rathena/conf/import/*`、`rathena/overlay-utf8/*` 等）を編集する。
2. **日本語 NPC / メッセージを変更した場合**は、apply する前に「日本語化の運用手順」の検証手順（`check-overlay.sh` → `check-jp-structure.sh` → `jp_english_audit.py`）を先に通す。
3. **ローカル smoke テストを実行する**（`app/` の変更が NPC 翻訳を伴わない場合も、設定ファイルの構文ミス等を検知できるので推奨）。
   ```sh
   scripts/local-smoke.sh --expect-npcs 13043
   ```
   colima（または Docker Desktop）でまっさらから起動し、map-server が healthy になり `[Error]`/`script error`/`npc_parse` が 0 行、NPC 総数が期待値と一致することを確認する。FAIL の場合は EC2 へ apply しない。
4. 変更内容を確認する。
   ```sh
   terraform -chdir=terraform plan
   ```
   `app/` の内容が変わると `archive_file` の md5 が変わり、S3 オブジェクトと SSM Association の差分として検出されます。
   **判定基準**: `destroy` 0 件・`replace` 0 件であること。`aws_s3_object.app` の `add`（作成）は、aws-nuke が毎晩 S3 オブジェクトを消すため**正常**です（次回 `apply` のたびに再アップロードされる想定）。それ以外の `add`/`destroy`/`replace` が出た場合は原因を確認してから進める（`aws_instance.app` や `aws_ebs_volume.data` の replace は特に注意。「インフラ変更」参照）。
5. 適用する。
   ```sh
   terraform -chdir=terraform apply
   ```
   S3 への再アップロード → SSM Association の再実行 → EC2 上で bundle 取得・rsync → `deploy.sh`（`.env` 同期 → `docker compose build --pull` → `systemctl restart ro-server`）まで自動で行われます。Association が `Success` になるまで `apply` 自体が待機します（`wait_for_success_timeout_seconds`。詳細は `README.md`「構築手順」）。
6. 反映を確認する。
   ```sh
   scripts/verify.sh
   ```
   - ポート到達性（6900/6121/5121 open）
   - `status.sh` の「map-server NPC パース」欄が 0 行であること
   - map-server ログに `Done loading '13043' NPCs`（現行の NPC 総数。上流 13037 + 独自 NPC 6）が出ていること（`scripts/logs.sh map-server --since 10m` で確認できる）
   - 各サービスが `healthy` であること
7. **再起動（反映）時刻を記録する**。次回の障害調査や「いつからこの挙動か」の切り分けに使うため、`terraform apply` を実行した日時をどこかに控えておく（Slack ログ・作業メモ等。本書には秘密情報を書かないこと以外の制約はない）。

### SSO 期限切れ時の対処

`terraform plan`/`apply` や `scripts/*.sh` の実行中に SSO トークンが切れると `refresh cached SSO token failed` 等のエラーになります。対処は 2 通りです。

1. **通常**: SSO に再ログインする。
   ```sh
   aws sso login --sso-session corp
   ```
2. **代替（`aws sso login` 自体が使えない/詰まる場合）**: 一時クレデンシャルをエクスポートして環境変数で渡し、Terraform には SSO プロファイル名を渡さないようにする。
   ```sh
   eval "$(aws configure export-credentials --profile sandbox-power --format env)"
   TF_VAR_profile="" terraform -chdir=terraform apply
   ```
   `terraform/variables.tf` の `profile` 変数（既定 `sandbox-power`）を空文字にすると、AWS プロバイダは `--profile` を使わず環境変数のクレデンシャルにフォールバックします。`scripts/lib/common.sh` 経由のスクリプト（`ssm_run` 等）も `AWS_PROFILE` 環境変数で同様に上書きできます。

## インフラ変更（`terraform/` 配下）

1. `terraform/*.tf` を編集する（命名は `local.name_fmt = "${project_name}-%s-${environment}"` に従うこと。個別ハードコードしない）。
2. リソースを追加する場合、`provider.default_tags`（`terraform/locals.tf` の `common_tags`）で `DoNotNuke` を含む必須タグが自動付与されることを確認する。`root_block_device` / `aws_ec2_tag`（ENI）/ DLM の `tags_to_add` は `default_tags` が伝播しないため、`common_tags` を明示的に merge する必要がある（既存コードの `aws_instance.app.root_block_device` 等を参照）。
3. `terraform -chdir=terraform plan` で意図しない削除・作り直し（特に `aws_instance.app` や `aws_ebs_volume.data` の replace）が含まれていないか確認する。**EC2 本体・data EBS の replace は行わないこと**（data EBS には DB データ・翻訳バックアップ・日次ダンプが載っており、作り直すとそれらが失われる。詳細は「障害時」の「EC2 再作成時の data EBS 引き継ぎ」を参照）。
4. `terraform -chdir=terraform apply`。

## 倍率変更

`app/rathena/conf/import/battle_conf.txt` を編集します。倍率はすべて percent 表記（100 = 1 倍）。現在の設定値は以下のとおりです（2026-09-24 反映分）。

| 設定キー | 現在値 | 倍率換算 | 対象 |
|---|---:|---:|---|
| `base_exp_rate` | 10000 | 100 倍 | Base EXP |
| `job_exp_rate` | 10000 | 100 倍 | Job EXP |
| `mvp_exp_rate` | 10000 | 100 倍 | MVP 撃破ボーナス EXP |
| `quest_exp_rate` | 10000 | 100 倍 | クエスト報酬 EXP |
| `item_rate_common` / `_heal` / `_use` / `_equip` | 500 | 5 倍 | 通常 Mob のアイテム/回復/消耗品/装備ドロップ |
| `item_rate_common_boss` / `_heal_boss` / `_use_boss` / `_equip_boss` | 10000 | 100 倍 | Boss Mob（カード以外） |
| `item_rate_common_mvp` / `_heal_mvp` / `_use_mvp` / `_equip_mvp` | 10000 | 100 倍 | MVP Mob（カード以外） |
| `item_rate_card` | 100000 | 1000 倍 | 通常カード（例: 0.01% → 10%） |
| `item_rate_card_boss` | 100000 | 1000 倍 | Boss カード |
| `item_rate_card_mvp` | 100000 | 1000 倍 | MVP カード |
| `item_rate_mvp` | 10000 | 100 倍 | MVP 報酬アイテム |
| `item_rate_adddrop` | 10000 | 100 倍 | 追加ドロップ（カード効果等） |
| `item_rate_treasure` | 10000 | 100 倍 | 宝箱 |
| `override_mob_names` | 2 | — | Mob 表示名（0=スポーン定義のまま/1=英語名固定/2=常に `mob_db` の JapaneseName。215 種のみ日本語、未収録は英語名にフォールバック） |

### 上限

ドロップ率の実際の上限は `item_drop_<種別>_max`（既定 10000 = 100%）で頭打ちになります。このリポジトリではこの上限キー自体は上書きしておらず、上流既定値（`conf/battle/drops.conf`）のままです。同様に `drops_by_luk`（LUK によるドロップ率補正。既定 0 = 無効）、`rare_drop_announce`（レアドロップの全体アナウンス。既定 0 = 無効）も上書きしていません。倍率を上げてもこれらの上限・挙動は変わらない点に注意してください。

### 変更 → 反映手順

「アプリ更新の標準手順」のとおり、`battle_conf.txt` を編集して `terraform -chdir=terraform apply` を実行します。この設定はビルド時にイメージへ焼き込まれるため、**EC2 上でファイルだけ書き換えて `docker compose restart` しても反映されません**。必ずリポジトリ側を編集して `apply`（再ビルドを伴う）してください。

### ゲーム内から現在値を確認する（`@rates`）

一般アカウント（group_id 0）でも使える GM コマンド `@rates` で、ログイン中のキャラクターから Base/Job EXP 倍率、通常/Boss/MVP のドロップ倍率をその場で確認できます（`mvp_exp_rate` / `quest_exp_rate` / `override_mob_names` は表示されません）。応答メッセージは `map_msg` 未翻訳のため英語表示です。

## アカウント運用

- パスワード変更: `RO_PASSWORD='...' scripts/set-password.sh <userid>`。値を SSM の実行パラメータに残したくない場合は `scripts/ssm-shell.sh` → `sudo /srv/ro-server/app/scripts/set-password.sh <userid>`（無エコー入力）。パスワードはどのログ・ドキュメントにも書かないこと。

作成（一般 / GM）:

```sh
scripts/create-account.sh <userid> <M|F>       # 一般（group_id 0）
scripts/create-account.sh <userid> <M|F> 99     # GM（group_id 99 = Admin）
```

一覧:

```sh
scripts/list-accounts.sh
```

各スクリプトの引数・環境変数・入出力の詳細は `docs/TOOLS.md`「1. `scripts/`」を参照してください。

### 既存アカウントの扱い

| account_id | userid | group_id | 用途 |
|---:|---|---:|---|
| 1 | （システム） | — | inter-server 用のシステムアカウント（`sex='S'`）。**触らない** |
| 2000000 | `admin01` | 99 | GM 検証用（未ログイン） |
| 2000001 | `player01` | 0 | 一般ユーザーの検証用 |
| 2000002 | `deltest01` | 0 | キャラクター削除検証用に作成。キャラクター 0 体のまま残置している検証専用アカウント（`tools/chardel_probe.py --delete` 等の破壊的操作の対象として使う） |

3 件とも `birthdate` は既定値 `2000-01-01`。初期パスワードは最終レビュー時にローテーション済みで記録していないため、利用前に `scripts/set-password.sh` で各自設定すること。

### 生年月日（キャラクター削除の確認コード）

PACKETVER 20211103 のクライアント（roBrowserLegacy 含む）は、キャラクター削除を「削除予約（0x0827）→ 生年月日 YYMMDD で確定（0x0829）」の 2 段階でしか行わず、rAthena の char-server は `char_del_option` の値に関係なく **必ず `login.birthdate` と照合**します（`src/char/char_clif.cpp` `chclif_parse_char_delete2_accept`。`char_del_option` の email 判定が効くのは 0x0068 / 0x01fb を送る旧クライアントだけ）。生年月日が NULL のアカウントは、このクライアントからはキャラクターを削除できません。

- `scripts/create-account.sh` は生年月日を必ず入れます（既定 `2000-01-01`。`RO_BIRTHDATE='YYYY-MM-DD'` で変更可）。作成時の出力に「削除の確認コード」として表示されます。
- 既存アカウントに後から設定する: `scripts/set-birthdate.sh <userid> [YYYY-MM-DD]`。NULL のアカウントにまとめて既定値を入れるなら `scripts/set-birthdate.sh --all-missing`（inter-server 用の account_id 1 は対象外）。変更は**次回 char-server ログインから有効**です。
- クライアント側の操作: キャラクター選択画面で削除 → 確認ダイアログ（roBrowserLegacy では msgstringtable の文言が「登録メールアドレスを入力してください」と出ますが、続くテキストボックスは生年月日入力です）→ **`YYYYMMDD`（既定なら `20000101`）** を入力。サーバには下 6 桁が届きます。
- サーバ側設定（`app/rathena/conf/import/char_conf.txt.tmpl`）: `char_del_option: 2`、`char_del_delay: 0`（予約直後に確定可。rAthena 既定は 24 時間待ち）、`char_del_restriction: 3`（パーティ / ギルド所属中は削除不可）。
- 削除は rAthena の正規処理（`char_delete()`）で行われ、inventory / cart / skill / friends / hotkey / char_reg 等の関連行も同時に消えます。DB を直接 DELETE する運用はしないこと。

### 既存アカウントの GM 昇格（作成スクリプトに昇格専用のオプションは無いため SQL で直接行う）

```sh
scripts/ssm-shell.sh
sudo -i
cd /opt/ro-server
printf "UPDATE \`login\` SET \`group_id\` = 99 WHERE \`userid\` = 'ここに対象の userid';\n" \
  | docker compose exec -T mariadb sh -c \
    'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'
```

`--default-character-set=utf8mb4` を付けること（rAthena 本体の接続は cp932 だが、テーブル自体は utf8mb4 のため、ホスト側スクリプトは utf8mb4 で接続する規約になっている）。`account_id = 1` は inter-server 用のシステムアカウント（`sex = 'S'`）なので変更しないこと。

## 独自 NPC（上流差し替えではない追加 NPC）

| NPC | 場所 | ファイル | 役割 |
|---|---|---|---|
| サポート職員 | prontera,160,180 | `npc/custom/jp/support.txt` | 全回復・主要都市への転送・サーバ説明 |
| 冒険者支援員（`TrainingSkipSupport`、修練場 5 面に duplicate） | new_1-1〜new_5-1,58,114（出現地点 53,111 のすぐ東） | `npc/custom/jp/training_skip.txt` | Novice 限定で一次職 6 職のいずれかへ即時転職: NV_BASIC 9 付与 → 未使用スキルポイント 0 → `F_ClearJobVar` → `Job_Change`（`jobchange`）→ 全回復（`percentheal 100,100` / `sc_end SC_ALL`）→ ノービスポーション 10 個 → セーブポイント prontera,117,72（±1）→ warp prontera,150,180。転職後は通常の転職と同じ JobLv 1 / JobExp 0 / Basic Skill 9 の状態になる。Novice 以外は「すでに職業についているため、このサービスは利用できません。」と表示して拒否する |

無効化したい場合は `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv` の該当行をコメントアウトして `tools/gen-jp-conf.py` → `terraform apply`。

## 日本語化の運用手順

サーバ側 NPC 日本語化の全体像・進捗・翻訳ルールは `docs/JP_TRANSLATION_RULES.md` / `docs/JP_NPC_PLAN.md` / `docs/JP_GLOSSARY.md` を参照してください。ここでは「実際に作業するときの手順」だけをまとめます。各ツールの引数・入出力の詳細は `docs/TOOLS.md`「3. `tools/`」を参照してください。

### (a) 新しい NPC ファイルを翻訳して追加する標準フロー

1. **バックアップを取る**（大きな変更の前は必須）。
   ```sh
   tools/jp-backup.sh before-<作業名>
   ```
2. 対象ファイルを翻訳する。配置は上流パスの鏡写し（`npc/cities/prontera.txt` → `app/rathena/overlay-utf8/npc/custom/jp/cities/prontera.txt`）。翻訳ルールは `docs/JP_TRANSLATION_RULES.md` に厳密に従う（文字列リテラルの中身だけを変更し、構造・識別子・比較値は変えない）。
3. `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv` に 1 行追記する（上流パス TAB 翻訳版パス）。
4. `scripts_custom.conf` の JP ブロックを再生成する。
   ```sh
   tools/gen-jp-conf.py
   ```
5. 構造検証を行う。
   ```sh
   scripts/check-jp-structure.sh --file <翻訳版パス> --upstream <上流パス>
   ```
   （MANIFEST 全件を流したい場合は引数なしで実行）
6. エンコーディング検証を行う。
   ```sh
   scripts/check-overlay.sh
   ```
7. 英語残りを監査する。
   ```sh
   tools/jp_english_audit.py --file <翻訳版パス>
   ```
   意図的に英語のまま残す文字列（アイテム名・URL 等）は `docs/jp-english-allowlist.tsv` に登録する。
8. ローカルスモークテストで実際に起動確認する。
   ```sh
   scripts/local-smoke.sh --expect-npcs <期待値>
   ```
   期待値は現行 NPC 総数（本書執筆時点 13043。追加した NPC 数に応じて変わる）。
9. 結果を `backups/jp-translation/` 配下にファイルとして保存する（各検証コマンドの出力をまとめてテキスト化。既存の `*-result-*.txt` の形式に倣う）。
10. すべて PASS したら「アプリ更新の標準手順」に従ってデプロイする。

### (b) 頭上表示名の付け方

rAthena は `表示名::ユニーク名` のうち exname（`::` の後ろ）だけで NPC を参照するため、頭上の表示名だけを `日本語#suffix::旧フル名` 形式に機械的に書き換えます。

```sh
tools/jp_npc_names.py inventory --out docs/jp-npc-names.tsv   # 棚卸し
# docs/jp-npc-names.tsv の apply_jp 列（人間が編集する唯一の列）を埋める
tools/jp_npc_names.py apply --map docs/jp-npc-names.tsv --dry-run   # 差分確認
tools/jp_npc_names.py apply --map docs/jp-npc-names.tsv             # 適用
tools/jp_npc_names.py check --map docs/jp-npc-names.tsv             # 整合検査
```

`docs/jp-npc-names.tsv` が Source of Truth です。NPC ファイル本体のヘッダ行を直接手編集しないこと。`apply_jp` には可視部分の日本語だけを書く（`#suffix` と exname はツールが上流ヘッダから引き継ぐ）。

### (c) 英語残りの監査と許容リスト

```sh
tools/jp_english_audit.py                     # MANIFEST 全件の候補一覧
tools/jp_english_audit.py --unused-allow       # 使われていない許容リスト行の確認（棚卸し用）
```

候補は「翻訳漏れ」か「意図的に英語のまま（アイテム名・URL・暗号パズル等）」のどちらかに分類し、後者は `docs/jp-english-allowlist.tsv` に `<file><TAB><pattern（正規表現）><TAB><理由>` で追記します。

### (d) Global_Functions の追加のみ方式

`app/rathena/overlay-utf8/npc/custom/jp/Global_Functions.txt` は上流の `Global_Functions.txt` を **`delnpc` で差し替えない**。差し替えると、上流ファイルの中から `F_x()` を直接呼び出している他ファイルのパースがスクリプトエラーになる（呼び出し元が先にロードされ、まだ関数が登録されていない状態で参照するため）。そのため翻訳版は MANIFEST に `追加のみ`（`delnpc` 無し）として登録し、翻訳したい関数だけを**同名で再定義して上書き**する方式を取っている（`npc_parse_function: Overwriting user function` という `[Info]` ログが出るが、これは想定どおりの動作でエラーではない）。新しい関数を日本語化する場合も、この「同名で追加する」方式を踏襲すること。

### (e) 復元

```sh
tools/jp-restore.sh --dry-run <backup-dir>   # 差分だけ確認
tools/jp-restore.sh <backup-dir>             # 復元（実行前に現状を自動退避）
```

`<backup-dir>` は `backups/jp-translation/<label>-<timestamp>`。復元後は `scripts/check-overlay.sh` / `scripts/check-jp-structure.sh` / `tools/gen-jp-conf.py --check` で整合を確認してから apply すること。

## 検証クライアント `tools/chardel_probe.py` の実務的な使い方

`tools/chardel_probe.py` は rAthena の実パケットを送ってキャラクター削除・NPC 会話（修練場スキップ）・map 入場を検証する最小クライアントです。オプションの全リストは `docs/TOOLS.md`「3. `tools/`」を参照してください。

### 実行場所

**必ず EC2 内から `--host 127.0.0.1` で実行してください。** Mac から EIP 越しに実行すると、同一 char セッションの 3 回目の要求に対する応答が届かず失敗する事象を確認しています（サーバ側は EC2 内からの同じ手順では全段階成功しており、実クライアントには影響していません）。

### EC2 への持ち込み方

`tools/` は `app/` の配布物に含まれないため、実行の都度 EC2 へ転送する必要があります。

- 対話シェルから配置する場合:
  ```sh
  scripts/ssm-shell.sh
  # 入った後、sudo -i してから任意の方法でファイル内容を作成する
  # （例: ローカルで base64 化した内容をペーストして base64 -d で復元する等）
  ```
- SSM Run Command で転送する場合: ファイルサイズが大きいため base64 化して分割し、複数回の `send-command` で `cat >>` していく（1 コマンドあたりの出力・入力サイズ制限に注意）。

### パスワードの扱い

パスワードは環境変数 `RO_PROBE_PASSWORD` から渡します（引数・ログ・JSON 出力のいずれにも残らない）。EC2 内で DB から直接値を取得して環境変数へ入れる運用にし、Mac 側の SSM 実行パラメータやシェル履歴にパスワードを残さないこと。

```sh
# EC2 内（例。実際の取得方法は対象アカウントに応じて調整する）
export RO_PROBE_PASSWORD='...'
```

### よく使うオプション

- `--npc-skip <job|decline|cancel>`: 修練場の「冒険者支援員」と会話して一次職転職を検証する。`job` は `acolyte|archer|mage|merchant|swordman|thief` のいずれか。
- `--delete`: キャラクター削除（0x0827 → 0x0829）を検証する。**破壊的操作**なので `deltest01` のような検証専用アカウントで使うこと。
- `--enter-map`: 残っているキャラクター 1 体で map まで入って即ログアウトする（map-server への到達確認）。
- `--cancel-reservation`: 削除予約の取り消し（0x082b）を検証する。
- `--keep`: `--delete` を無効化する（作成だけ試したいとき等）。
- `--verbose` / `-v`: パケットトレースを stderr に出す（デバッグ用。ログに残す運用はしない）。

## ログ調査

### CloudWatch Logs（ローカルから）

```sh
scripts/logs.sh map-server --since 1h
```

`login-server` / `char-server` / `map-server` / `mariadb` の 4 ストリーム、保持 14 日。「日常確認」の healthcheck ノイズ（10 秒ごとの `Closed connection from 127.0.0.1`）は読み飛ばすこと。

### DB のログテーブル

現在の設定（`app/rathena/conf/import/log_conf.txt` で `sql_logs: yes` / `log_commands: yes` のみ上書き、それ以外は上流既定値 `conf/log_athena.conf` のまま）では、以下のテーブルが実際にデータを持ちます。

| テーブル | 内容 | 記録条件 |
|---|---|---|
| `loginlog` | ログイン試行の記録（成功/失敗理由コード） | 常時 |
| `charlog` | キャラクター選択・作成等のイベント | 常時 |
| `atcommandlog` | GM コマンド（`@`/`#`）の実行履歴 | `log_commands: yes` かつ実行者の group が `conf/groups.yml` で `LogCommands: true`（Id 99 Admin は該当）。2026-09-24 時点 0 件（GM コマンド未実行） |
| `npclog` | NPC スクリプトの `logmes` コマンド実行 | `log_npc: yes`（既定で有効） |
| `picklog` | アイテムの入手/消費/破棄等 | `enable_logs: 0xFFFFFFFF` / `log_filter: 1`（既定で全種類・全アイテムが対象） |

以下は**既定で無効**（このリポジトリで有効化する上書きはしていない）のため、通常は空です。調査したい場合は `app/rathena/conf/import/log_conf.txt` に該当キーを追記して再デプロイする。

| テーブル | 内容 | 既定 |
|---|---|---|
| `zenylog` | Zeny の増減 | `log_zeny: 0`（無効） |
| `mvplog` | MVP 撃破記録（`picklog` の type `U` と重複するため非推奨扱い） | `log_mvpdrop: no`（無効） |
| `chatlog` | チャット内容（グローバル/ウィスパー/パーティ/ギルド 等） | `log_chat: 0`（無効） |

DB へ SQL を投げる場合は EC2 内から実行します（rAthena 本体の接続は cp932 だが、テーブル自体は utf8mb4 なので `--default-character-set=utf8mb4` を付ける）。

```sh
scripts/ssm-shell.sh
sudo -i
cd /opt/ro-server

# 直近の GM コマンド実行履歴
printf "SELECT atcommand_date, char_name, map, command FROM atcommandlog ORDER BY atcommand_id DESC LIMIT 20;\n" \
  | docker compose exec -T mariadb sh -c \
    'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --table --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'

# 直近のログイン試行（rcode は AC_REFUSE_LOGIN の error コードに相当。0=成功系）
printf "SELECT time, ip, user, rcode, log FROM loginlog ORDER BY time DESC LIMIT 20;\n" \
  | docker compose exec -T mariadb sh -c \
    'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --table --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'

# 直近のキャラクター選択/作成イベント
printf "SELECT time, char_msg, account_id, name FROM charlog ORDER BY id DESC LIMIT 20;\n" \
  | docker compose exec -T mariadb sh -c \
    'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --table --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'
```

### OS / アプリログ

- `journalctl -u ro-server.service` / `journalctl -u ro-server-backup.service`（EC2 上）: systemd unit のログ。
- `/var/log/ro-server-deploy.log`（EC2 上）: SSM Association / `deploy.sh` の実行ログ。
- rAthena 本体の生ログ: コンテナ内では標準出力（`docker compose logs`）に出るが CP932→UTF-8 変換込みで CloudWatch にも同時に出る（dual logging）。rAthena 標準の `log/` 配下フラットファイルは `sql_logs: yes` のため使っていない（DB ログテーブルを参照）。

## バックアップ・リストア詳細

| 種別 | 方法 | スケジュール / 保持 | 備考 |
|---|---|---|---|
| EBS スナップショット | DLM `legacy-app-lab-data-dlm-verify`（`DlmBackup=legacy-app-lab-data-verify` タグの data EBS が対象） | 毎日 19:30 UTC（04:30 JST）、7 世代 | スナップショットには `tags_to_add` により `DoNotNuke=true` を含む共通タグと `Name` が付くため aws-nuke の削除対象外（`copy_tags` は無効。有効にすると `Name` が重複して CreateSnapshot が失敗する）。DLM ポリシー自体は aws-nuke にリソースタイプが無い |
| DB ダンプ（自動） | `ro-server-backup.timer` → `mariadb-dump --single-transaction --quick --routines --events` | 毎日 04:00 JST、`/srv/ro-server/backups/` に 7 日分（`ragnarok-*.sql.gz`） | data EBS 上なのでインスタンス再作成後も残る |
| DB ダンプ（即時） | `scripts/backup-db.sh` | 任意 | 中身が 1KB 未満、または `CREATE TABLE` を含まない場合はダンプ失敗として扱われる |
| DB リストア | `app/scripts/restore-db.sh <dump file>`（EC2 上・root） | — | login/char/map を停止 → リストア → 起動。確認プロンプトあり（`FORCE=1` で省略可） |
| 翻訳スナップショット | `tools/jp-backup.sh <label>` | 作業のたびに手動 | `backups/jp-translation/<label>-<timestamp>/` に `overlay-utf8/` 全体・MANIFEST・ツール一式・ハッシュを保存。復元は `tools/jp-restore.sh`。DB とは別系統（NPC 翻訳ファイルのみ） |

リストア手順:

```sh
scripts/ssm-shell.sh
sudo -i
cd /opt/ro-server
ls -lh /srv/ro-server/backups/
scripts/restore-db.sh /srv/ro-server/backups/ragnarok-YYYYmmdd-HHMMSS.sql.gz
```

EBS スナップショットからの全体復旧（DB ダンプでは不十分な障害時）: DLM のスナップショットから新規ボリュームを作成し、既存の data EBS（`legacy-app-lab-data-ebs-verify`）と差し替える。Terraform 管理下のリソースを手動操作で差し替えることになるため、実施前に影響範囲（state との整合）を確認すること。定型手順は未整備。

## 再起動

```sh
aws --profile sandbox-power ec2 reboot-instances --instance-ids i-03f3599d032bd7000
```

`ro-server.service` は `systemctl enable` 済みのため、OS 起動時に自動的に `docker compose up -d --remove-orphans` が実行されます（`ExecStartPre` で `update-public-ip.sh` が先に走り、IMDSv2 から取得した Public IP を `.env` に反映してから起動する）。

再起動後の復旧確認:

```sh
# 数分待ってから
scripts/verify.sh
```

## 障害時

**個別サービスの再起動**（EC2 上）:

```sh
cd /opt/ro-server
docker compose restart login-server
docker compose restart char-server
docker compose restart map-server
docker compose restart mariadb
```

依存関係は `mariadb` → `login-server` → `char-server` → `map-server` の順（`docker-compose.yml` の `depends_on` / healthcheck）。下位のサービスを再起動すると上位のサービスも接続し直しが必要になる場合がある。

**DB 破損時**: 「バックアップ・リストア詳細」の手順で最新のダンプからリストアする。ダンプでも復旧できない場合は DLM スナップショットからの EBS 復旧を検討する。

**外部からポートに到達できない場合**: `scripts/verify.sh` で NG が出た場合、まずコンテナ側（`docker compose ps`）を確認し、正常起動しているのに到達できないときは Security Group のルールが変わっていないか確認する。

```sh
aws --profile sandbox-power ec2 describe-security-groups --group-ids sg-080a678ceda19ff70
```

6900/6121/5121 の 3 本の ingress（`0.0.0.0/0`）が揃っているかを見る。Terraform 管理下のリソースなので、差分があれば手動で戻さず `terraform plan`/`apply` で意図した状態に戻すこと。

**EC2 再作成時の data EBS 引き継ぎ**: `/srv/ro-server`（data EBS）配下には `app/`（`.env` を含む）、`mariadb/`（DB データ）、`backups/` が全て乗っている。EC2 インスタンスだけを作り直し、同じ data EBS を再アタッチすれば、**`.env`（秘密情報）と DB データはそのまま引き継がれる**。ただし `terraform destroy` は data EBS 自体も削除するため、この引き継ぎが有効なのはインスタンスのみを個別に作り直すケース（例: `terraform taint`/`-replace` で `aws_instance.app` のみ再作成する場合）に限られる。

## aws-nuke との付き合い方

**運用ルール: nuke 後（毎朝 05:00 JST 以降）に再デプロイ・強制再実行が必要な場合は、必ず `terraform -chdir=terraform apply` を経由すること。** S3 の `app.zip` は毎晩消えるため、association 単独の再実行（`start-associations-once`、`deployed.md5` 削除後の再適用など）はオブジェクト不在で失敗しうる。`terraform apply` は `app.zip` を再作成してから association を適用する。稼働中のサーバは `app.zip` の有無に影響されない（アプリはデータボリューム上にあり、配布済み md5 が一致していれば association の再実行は「nothing to do」で成功する。2026-09-23 に実測）。


- 毎日 **05:00 JST** に Sandbox アカウント全体で aws-nuke（no-dry-run）が走る。`DoNotNuke=true` タグの付いたリソースは除外されるが、**このタグは `provider.default_tags` 経由でしか自動付与されない**ため、Terraform 管理外で手動作成したリソースには必ず個別にタグを付けること。
- 05:00 JST 以降は「日常確認」の `scripts/verify.sh` を実行し、想定外の削除が起きていないか確認する習慣を付けること。
- dry-run では EC2 プライマリ ENI（`legacy-app-lab-eni-verify`）が削除候補に表示される（aws-nuke v3.46.1 が ENI のタグを読まないため）。2026-09-23 05:00 JST の本番実行ログでは ENI は対象に上がらず削除試行も無かったが、仮に試行されてもプライマリ ENI はデタッチ不可のため無害。S3 の `app.zip` / `ssm-output/` が消えるのも想定どおり（次回 `terraform apply` で再作成される）。
- **S3 バケット内のオブジェクトはタグで保護できない**（バケット自体は保護されるが中身は毎晩消える）。配布用バケット（`legacy-app-lab-deploy-s3-verify`）は `apply` のたびに Terraform が再アップロードする前提で運用しているため実害はないが、**このバケットや他の新規 S3 バケットに永続データ（DB ダンプ、state 等）を置かないこと**。
- Terraform state もこの理由でローカル保持としている（S3 backend は使わない）。

## 撤去手順

```sh
terraform -chdir=terraform destroy
```

- VPC / EC2 / EBS（root・data 双方）/ S3 / CloudWatch Logs / IAM ロール等ほぼ全リソースが削除される。
- **DLM が作成済みの EBS スナップショットは残る**。不要であれば個別に削除する（`aws --profile sandbox-power ec2 describe-snapshots` → `delete-snapshot`）。
- `.env` に保存されていた秘密情報は EC2/EBS と共に失われる。撤去前に必要なデータ（最新 DB ダンプ等）は退避しておくこと。

## 既知の制限

- **日本語化は導線の一部のみ**: サーバ側で翻訳済みなのは `app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv` に載っている 148 ファイル（上流差し替え 146 + 追加のみ 2）・mes 49,578 行。Pre-RE でロードされる全 527 ファイル・約 18 万 mes 行のうち約 3 割弱（ファイル数）で、主にフェイヨン系クエスト、転職導線の残り、日常 NPC 小物、Ep.10 以降の街クエストは英語のまま（詳細は `docs/JP_NPC_PLAN.md`）。
- **頭上表示名**: 可視 NPC 1,108 体中 1,099 体を日本語化済み。`strnpcinfo(1)` 比較に使われる一部（Merchant of Manuk/Splendide 等）と内部識別子用の NPC は英語のまま維持している。
- **Mob 名は初期セットのみ**: 約 215 種のみ日本語名が設定されており、未収録の Mob は英語名で表示される。追加は `app/rathena/overlay-utf8/db/import/mob_db.yml` への追記で対応可能。
- **GM コマンド応答は英語**: `map_msg` は 214 件のみ翻訳済み。`@rates` 等のシステムメッセージは英語表示。
- **アイテム名・スキル名・マップ名**: `getitemname()` 等はサーバの `item_db` 英語名がそのまま出る（意図的な範囲。`docs/JP_TRANSLATION_RULES.md` 参照）。
- **web-server 未起動**: ギルドエンブレム等の一部クライアント機能が動作しない（通常プレイには影響しない設計判断。`docs/DESIGN.md` §7 参照）。
- **IME 未検証**: 自由入力を要するクイズ（bard 歌詞、プロンテラ伝承歌、alchemist_skills 試験）は日本語 IME 入力前提だが実機検証は未実施。

## トラブルシューティング集

| 症状 | 原因 | 対処 |
|---|---|---|
| map-server が起動時に SIGSEGV で落ちる（NPC 翻訳後、再現は不定） | `parse_variable()` の添字式 `var[...]` 走査が文字列も 2 バイト文字も見ない生バイト走査のため、添字の中の文字列に CP932 で 2 バイト目が `[`(0x5B)/`]`(0x5D) になる文字（「ー」「ゼ」「ゾ」「‐」等、計 104 字）が入っているとファイル末尾を越えて読み進んでしまう | `scripts/check-jp-structure.sh` の検査 1c で検出できる（apply 前に必ず通す）。該当箇所は言い換えず英語表記にする（`getitemname()` が英語なので整合する）。詳細は `docs/JP_TRANSLATION_RULES.md` |
| `Global_Functions.txt` を差し替えた翻訳版に入れ替えたら map-server 起動時に `script error` | `Global_Functions.txt` を `delnpc` で丸ごと差し替えると、他ファイルからの `F_x()` 直接呼び出しがロード順の関係でパース時エラーになる | `delnpc` せず「追加のみ・同名で関数を再定義して上書き」方式にする（現行の `npc/custom/jp/Global_Functions.txt` を参照）。`npc_parse_function: Overwriting user function` の `[Info]` ログは正常 |
| ローカル colima 検証で DB が起動しない・`crashed` 扱いになる | ローカル検証 DB（`app/.local/mariadb`、MyISAM）が不正終了すると crashed マークが付くことがある | `scripts/local-smoke.sh` は毎回 `./.local/` を削除してから起動するので通常は自然に解消する。`docker compose` を直接使う手動検証で発生した場合は `app/.local/` を削除して作り直す |
| `terraform plan`/`apply` が `refresh cached SSO token failed` で失敗する | SSO セッションの期限切れ | `aws sso login --sso-session corp`、または `eval "$(aws configure export-credentials --profile sandbox-power --format env)"` の上で `TF_VAR_profile="" terraform ...` を実行する（「アプリ更新の標準手順」参照） |
| aws-nuke（毎朝 05:00 JST）直後に SSM Association を再実行すると失敗する | S3 の `app.zip` が毎晩削除されるため、association 単独の再実行だとオブジェクト不在で失敗する | 「aws-nuke との付き合い方」のとおり、association 単独ではなく必ず `terraform -chdir=terraform apply` を経由する（`app.zip` を再アップロードしてから association を適用する） |
| ログインしようとすると `result=8` で拒否される | rAthena login-server は「そのアカウントが既にオンライン扱い」と判定すると `result=8`（`AUTH_TIMEOUT`＝30 秒のタイマーで旧セッションの強制切断を試みつつ拒否）を返す。前回の接続が異常終了（クライアントのクラッシュ、`chardel_probe.py` の異常終了等）してサーバ側のオンライン状態が残っていると発生する | 30 秒程度待ってから再ログインする（旧セッションが自動的に解放される）。急ぎの場合は EC2 上で該当アカウントの char-server 接続状況を確認する |
| キャラクター削除確定（0x0829）が `result=5` で失敗する | `HC_DELETE_CHAR3` の `result=5` は「生年月日が一致しない」（`login.birthdate` とクライアント入力の下 6 桁 YYMMDD の不一致） | 対象アカウントの生年月日を `scripts/list-accounts.sh` や DB 参照で確認し、クライアントには `YYYYMMDD`（既定なら `20000101`）を正しく入力する。生年月日を変更した直後は次回 char-server ログインから有効になる点に注意（「アカウント運用」参照） |
