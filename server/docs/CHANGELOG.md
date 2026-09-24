# 変更履歴

日付は JST。種別: 構築 / 設定変更 / 日本語化 / 機能追加 / 障害対応 / ドキュメント。

## 2026-09-22

- **種別**: 構築
- **内容**: 設計（`docs/DESIGN.md`）、AWS Sandbox の事前調査（VPC 0 個・aws-nuke の仕組みと落とし穴の洗い出し）、`nuke-config.yaml` への `EC2InternetGatewayAttachment` 例外（`tag:vpc:DoNotNuke`/`tag:igw:DoNotNuke`）追記、初回 `terraform apply`。
- **影響**: 新規構築（初回起動）。apply 時に、Sandbox の SCP により S3 バケットの `PutBucketPublicAccessBlock` が拒否されること（実効値は公開ブロック全 true）、AL2023 同梱の Docker Buildx（0.12 系）が Docker Compose v5 の `build`（buildx ≥ 0.17 必須）に対応しておらず buildx v0.37.1 を別途配置する必要があることが判明し、対応済み。
- **関連ファイル**: `docs/DESIGN.md` §1・§3.1・§4.2、`docs/nuke/`

## 2026-09-23 00:37 頃

- **種別**: 構築
- **内容**: サーバ構築完了。最終レビューとして admin01 / player01 のパスワードをローテーション、DLM の `copy_tags` を修正（`Name` タグ重複で `CreateSnapshot` が失敗するため無効化し `tags_to_add` で明示付与に変更）、Mob 名の修正、CP932 往復テスト（`app/rathena/tests/cp932_roundtrip.c`）を実施。
- **影響**: 初回構築完了。以降の設定変更・日本語化はいずれも `terraform apply`（再ビルド）を伴う。
- **関連ファイル**: `terraform/backup.tf`、`app/rathena/tests/cp932_roundtrip.c`

## 2026-09-23 20:13〜23:26 JST NPC 日本語化 Batch 1〜5

- **種別**: 日本語化
- **内容**: `docs/JP_NPC_PLAN.md` の優先順位に基づき Batch 1〜5 を実施。各 Batch とも構造検証（`check-jp-structure.sh`）・CP932 変換検証・ローカル起動スモークが PASS。
  - **Batch 1**（20:13）: 21 ファイル・4,855 mes。主要都市の住人・案内係・商人・掲示板・修練場。結果 `backups/jp-translation/batch-1-result-20260923-201353.txt`
  - **Batch 2**（21:34）: 33 ファイル・7,060 mes。ゲフェン/フェイヨン/アルデバラン/コモド/ジュノー、モロク、美容師・染色屋・スロット付与 等。結果 `backups/jp-translation/batch-2-result-20260923-213428.txt`。**`merchants/elemental_trader.txt` の添字式内の「ー」（CP932 0x815B）が `[` と誤認され、map-server が起動時に SIGSEGV する rAthena `parse_variable()` の制約を発見**（再現はヒープ配置依存で不定）。該当箇所を英語表記に修正し、`tools/jp_structure_check.py` に検査 1c（添字走査）を追加。
  - **Batch 3**（22:13）: 14 ファイル・10,816 mes。二次職転職クエスト 2-1/2-2 全 13 職 + 転生バルキリー。結果 `backups/jp-translation/batch-3-result-20260923-221300.txt`
  - **Batch 4**（22:43）: 20 ファイル・9,002 mes。プラチナスキルクエスト（`npc/quests/skills/*`）。結果 `backups/jp-translation/batch-4-result-20260923-224345.txt`
  - **Batch 5**（23:25）: 18 ファイル・8,353 mes。初期都市クエスト 9（prontera/alberta/geffen/payon/izlude/aldebaran/lutie/comodo/yuno）+ イズルードアリーナ 9。結果 `backups/jp-translation/batch-5-result-20260923-232545.txt`
  - 構築時点で既に翻訳済みだった初期セット 11 ファイル（2,042 mes）と合わせて、合計 117 ファイル・42,128 mes。
- **影響**: 23:26 JST に `terraform apply` で Sandbox へ再デプロイ（再ビルド）。
- **関連ファイル**: `docs/JP_NPC_PLAN.md` §4、`app/rathena/overlay-utf8/npc/custom/jp/`、`backups/jp-translation/batch-{1..5}-result-*.txt`、開始前バックアップ `backups/jp-translation/before-batch-N-*/`、最終スナップショット `backups/jp-translation/after-batch-5-20260923-232547/`

## 2026-09-23 23:43 JST

- **種別**: 障害対応
- **内容**: キャラクター削除ができない問題を調査・修正。原因は、PACKETVER 20211103 クライアント（roBrowserLegacy 含む）の削除確定（0x0829）が `char_del_option` の値に関係なく `login.birthdate` と照合される仕様（`chclif_parse_char_delete2_accept`。email 判定が効くのは 0x0068/0x01fb を送る旧クライアントのみ）のため、birthdate が NULL のアカウントは削除できなかったこと。`scripts/create-account.sh` に生年月日の既定値（`2000-01-01`。`RO_BIRTHDATE` で変更可）を導入し、`char_del_delay: 0` に設定（rAthena 既定は 24 時間待ち）。既存アカウントへ後付けする `scripts/set-birthdate.sh` と、検証用の `tools/chardel_probe.py`（実パケットで login→char→map を実行する最小クライアント）を追加。
- **影響**: `char_conf.txt.tmpl` の変更を含むため `terraform apply`（再ビルド）で反映。
- **関連ファイル**: `docs/OPERATIONS.md`「キャラクター削除と生年月日」、`app/scripts/create-account.sh`、`scripts/set-birthdate.sh`、`tools/chardel_probe.py`、`app/rathena/conf/import/char_conf.txt.tmpl`

## 2026-09-24 00:48〜02:10 JST 日本語化 第 2 フェーズ

- **種別**: 日本語化
- **内容**: 開始前スナップショット `backups/jp-translation/before-npc-name-phase2-20260924-004816/` を取得し、Phase A/B/C を実施（結果ファイルのタイムスタンプに基づく実行順は B → A → C）。各 Phase とも構造検証 PASS・CP932 OK・`gen-jp-conf.py --check` 差分なし・ローカル起動 13037 NPC / エラー 0 を確認。
  - **Phase B**（01:18、英語残りの監査・修正）: `tools/jp_english_audit.py` で 117 ファイル内の英語残りを監査（初回 278 件→許容リスト `docs/jp-english-allowlist.tsv` 適用後 13 件→修正後 0 件）。waitingroom タイトル 16 件等、18 行 / 17 ファイルを修正。結果 `backups/jp-translation/phase2-B-result-20260924-011808.txt`
  - **Phase A**（01:37、頭上表示名）: NPC ヘッダを `日本語#suffix::旧フル名` 方式に書き換え、704 体の頭上表示名を日本語化（exname は不変。対応表 `docs/jp-npc-names.tsv`）。内部識別子・不可視相当（Manager#hnt 等）と `strnpcinfo(1)` 比較に使われる NPC 名（Merchant of Manuk / Merchant of Splendide）は英語のまま維持。結果 `backups/jp-translation/phase2-A-result-20260924-013750.txt`
  - **Phase C**（01:57、追加翻訳）: 通常プレイ導線の追加翻訳 30 ファイル（1 次職チュートリアル `tu_*` 7 本、モロク街、DTS 転送、中和剤、傭兵レンタル、スキルリセット、ジュース、ミスタースマイル、バニーバンド、`Global_Functions.txt` の部位名関数 3 つ、shops 2 本）+ 頭上名 343 体 + duplicate 依存で再登録していた上流 12 ファイルを翻訳版へ切替。`Global_Functions.txt` は `delnpc` せず「追加のみ」で読み込ませ、同名関数を上書き（直接呼び出し構文がパース時に関数定義を要求するため）。結果 `backups/jp-translation/phase2-C-result-20260924-015731.txt`
  - 完了時点: MANIFEST 147 エントリ・mes 49,544 行。
- **影響**: 02:10 JST に `terraform apply` で Sandbox へ再デプロイ（再ビルド）。
- **関連ファイル**: `docs/JP_NPC_PLAN.md` §5、`docs/jp-npc-names.tsv`、`docs/jp-english-allowlist.tsv`、`tools/jp_npc_names.py`、`tools/jp_english_audit.py`、最終スナップショット `backups/jp-translation/after-phase2-*/`

## 2026-09-24 14:08 JST

- **種別**: 設定変更
- **内容**: 倍率を再変更。Base EXP / Job EXP を `1000`（10 倍）→ `10000`（100 倍）、MVP EXP / クエスト EXP を `100`（等倍）→ `10000`（100 倍）、通常カード `item_rate_card` を `10000`（100 倍）→ `100000`（1000 倍。Poring Card 0.01% → 10.00%）、Boss/MVP カード `item_rate_card_boss` / `card_mvp` を `1000`（10 倍）→ `100000`（1000 倍）、Boss/MVP（カード以外）・MVP 報酬・追加ドロップ・宝箱（`item_rate_*_boss` / `*_mvp` / `mvp` / `adddrop` / `treasure`）を `100`（等倍）→ `10000`（100 倍）に変更。通常アイテム 5 倍（`item_rate_common` 等 `500`）は変更なし。
- **影響**: `battle_conf.txt` はビルド時にイメージへ焼き込まれるため、`terraform apply`（再ビルドを伴う）で反映。
- **関連ファイル**: `app/rathena/conf/import/battle_conf.txt`、`docs/OPERATIONS.md`「倍率変更」

## 2026-09-24 14:56 JST

- **種別**: 機能追加
- **内容**: 独自 NPC「冒険者支援員」（`npc/custom/jp/training_skip.txt`、テンプレート `冒険者支援員::TrainingSkipSupport` + new_1-1〜new_5-1,58,114 の duplicate）を追加。初心者修練場内、出現地点（53,111）のすぐ東に配置。Novice 限定で一次職 6 職へ即時転職（NV_BASIC 9 付与 → SkillPoint 0 → `F_ClearJobVar` → `Job_Change`（`jobchange`）→ percentheal 100,100 / `sc_end SC_ALL` → ノービスポーション 10 個 → savepoint prontera,117,72 → warp prontera,150,180）。Novice 以外は「すでに職業についているため、このサービスは利用できません。」と表示し拒否。6 職・辞退・キャンセル・再訪拒否・再ログインを実機でテスト済み。MANIFEST は「追加のみ」のエントリとして登録し 148 エントリ・mes 49,578 行に到達。
- **影響**: NPC 総数が 13037 → 13043 に増加（上流 13037 + 独自 NPC 6: サポート職員 1 + 冒険者支援員の修練場 5 面分 duplicate 5）。`terraform apply` で再デプロイ（再ビルド）。
- **関連ファイル**: `app/rathena/overlay-utf8/npc/custom/jp/training_skip.txt`、`app/rathena/overlay-utf8/npc/custom/jp/MANIFEST.tsv`、`docs/OPERATIONS.md`「検証サーバ独自の追加 NPC」

## 2026-09-24 ドキュメント整備

- **種別**: ドキュメント
- **内容**: 文書体系を整理。新規: `docs/SPEC.md`（現行仕様書。設定値・数値・根拠ファイルを併記した Source of Truth）、`docs/TOOLS.md`（全スクリプト・ツールのリファレンス）、`docs/CHANGELOG.md`（本ファイル）。全面見直し: `README.md`（現状表・文書一覧・リポジトリ構成を現行化）、`docs/OPERATIONS.md`（アプリ更新の標準手順、日本語化の運用手順、検証クライアントの使い方、トラブルシューティング集を追加）。更新: `docs/DESIGN.md`（v0.5）、`CLIENT_HANDOFF.md`（実機確認済み項目、冒険者支援員）、`docs/JP_NPC_PLAN.md`（Phase 2 完了後の数値、ロード対象 527 ファイルへ訂正）、`docs/JP_TRANSLATION_RULES.md`（上流原本の取得方法）。あわせて `scripts/local-smoke.sh` のヘッダ例と `tools/jp-backup.sh` が生成する復元手順の `--expect-npcs` 例を 13043 に修正（動作変更なし）。
- **影響**: なし（ドキュメントとコメントのみ、サーバへの変更なし）。
- **関連ファイル**: `README.md`、`docs/SPEC.md`、`docs/OPERATIONS.md`、`docs/TOOLS.md`、`docs/DESIGN.md`、`CLIENT_HANDOFF.md`、`docs/JP_NPC_PLAN.md`、`docs/JP_TRANSLATION_RULES.md`

## 2026-09-24 リポジトリ統合に向けた文書整理（Phase 1）

- **種別**: ドキュメント
- **内容**: Phase 2 で本リポジトリを GitHub の RO-Labo リポジトリへ `server/` として統合する計画に合わせ、文書間の参照を整理。`README.md` を server の入口として縮約（詳細手順は `docs/OPERATIONS.md` / `docs/TOOLS.md` / `docs/SPEC.md` / `docs/DESIGN.md` へのリンクに置き換え）。`CLIENT_HANDOFF.md` は kRO ネイティブクライアント + WARP 前提の文書として HISTORICAL 化（先頭に注記を追加、本文は未変更）。`docs/SPEC.md`（関連文書表・§12）と `docs/JP_NPC_PLAN.md`（§3.5 相当箇所）のクライアント側参照を `CLIENT_HANDOFF.md` から RO-Labo リポジトリ側の文書（`client/README.md` / `docs/CURRENT_STATUS.md`）へ変更。あわせて RO-Labo 側にルート README・`docs/ARCHITECTURE.md`・`docs/CURRENT_STATUS.md`・`client/README.md` 等を新設（実際に稼働しているクライアントは roBrowserLegacy + ro-glue であり、CLIENT_HANDOFF が前提にしていたネイティブクライアントではないため）。
- **影響**: なし（ドキュメントの参照整理のみ。`app/` `terraform/` `scripts/` `tools/` への変更なし）。
- **関連ファイル**: `README.md`、`CLIENT_HANDOFF.md`、`docs/SPEC.md`、`docs/JP_NPC_PLAN.md`（RO-Labo リポジトリ側: ルート `README.md`、`docs/ARCHITECTURE.md`、`docs/CURRENT_STATUS.md`、`client/README.md`）

## 2026-09-24 RO-Labo への統合（Phase 2）

- **種別**: ドキュメント / 構成
- **内容**: ro-server を RO-Labo の `server/` として統合、`CLIENT_HANDOFF.md` を `notes/archive/` へ移動、クライアント側 `tools/` を `client/` へ移動、文書のパス更新。サーバの runtime / Terraform / スクリプトは無変更。Terraform state 等は Git 管理外のまま。
- **影響**: なし。
- **関連ファイル**: `README.md`、`NOTICE.md`、`docs/ARCHITECTURE.md`、`docs/CURRENT_STATUS.md`、`client/README.md`、`client/docs/`、`notes/archive/`（RO-Labo リポジトリ側）、`server/README.md`、`server/docs/SPEC.md`、`server/docs/OPERATIONS.md`、`server/docs/TOOLS.md`、`server/docs/DESIGN.md`、`server/docs/JP_NPC_PLAN.md`、`server/docs/CHANGELOG.md`（本ファイル）

---

## 今後の予定・未対応

- **未翻訳範囲**: Pre-RE ロード対象 527 ファイル中、148 ファイルが日本語化対応済み。残りは主にフェイヨン系クエスト、転職導線の残り、日常 NPC 小物、Ep.10 以降の街クエスト（約 7 万 mes）、飛空艇・結婚・ミニゲーム・図書館・拡張職・WoE 城。詳細は `docs/JP_NPC_PLAN.md`、棚卸しは `docs/JP_COVERAGE_PHASE2.md`。
- **SystemCode が暫定値**: `00-01-01` は Sandbox 既存 SRE リソースの前例に合わせた暫定値。正式なシステムコードの確定が必要。
- **EC2 の CPU credit が unlimited のまま**: 推奨は `standard` だが未変更。
- **職業別の初期装備配布**: 未実装。
- **DLM スナップショット取得の確認**: 2026-09-24 04:30 JST 以降分の取得確認が未実施。
