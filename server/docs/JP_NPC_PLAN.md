# NPC 日本語化 拡張計画（Pre-Renewal 導線優先）

現行の状態は `docs/SPEC.md` §8、作業手順は `docs/OPERATIONS.md` を参照。

- 作成: 2026-09-23（rAthena `e985006`、Pre-RE ロード対象の棚卸しに基づく）
- 方針: rAthena 本体は無改変 / `app/rathena/overlay-utf8/npc/custom/jp/` に翻訳版を置く / `npc/scripts_custom.conf` で `delnpc:` → `npc:` 差し替え / Git は UTF-8・ビルド時に CP932 変換

## 1. 現状（Pre-RE で実際にロードされる NPC の全量）

`npc/pre-re/scripts_main.conf` を再帰展開した結果: **527 ファイル / 380,429 行 / `mes` 181,804 行**（ファイル数は 2026-09-24 に上流 `e985006` で再集計。当初の 522 は集計漏れ）。
翻訳済みは 10 ファイル・`mes` 2,013 行（**1.1%**）。「NPC に話しかけると英語のまま」はこの未翻訳分（サーバ側）で、クライアント側の問題ではない。

| ディレクトリ | ファイル | `mes` 行 | 備考 |
|---|---:|---:|---|
| `npc/quests/` | 86 | 128,602 | 全体の 71%。街別クエスト。後期エピソード（Lighthalzen/Rachel/Veins/Hugel/Moscovia/Nameless/13.x）が大半 |
| `npc/jobs/` | 33 | 14,288 | 2 次職・拡張職・転生 |
| `npc/cities/` | 26 | 12,515 | 街の住人（雑談・小ネタ・一部クエスト導入） |
| `npc/other/` | 29 | 9,856 | 本、モンスターレース、ターボトラック、結婚、闘技場、PvP、掲示板 等 |
| `npc/quests/skills/` | 21 | 9,002 | プラチナスキル（各職の追加スキルクエスト） |
| `npc/pre-re/jobs/` | 9 | 3,419 | 1 次職（6 本翻訳済み）+ 修練場 |
| `npc/merchants/` + `pre-re/merchants/` | 29 | 3,034 | 精錬・宿屋・レンタル・髪型・染色・交換 等（純粋な `shop` は文字列なし） |
| `npc/pre-re/quests/` | 16 | 1,714 | Pre-RE 版のモロク街（1,597）ほか |
| `npc/pre-re/guides/` | 21 | 1,575 | 街案内（プロンテラ翻訳済み） |
| `npc/guild/` + `guild2/` | 35 | 1,250 | WoE（砦管理 NPC 等。システム寄りで文字列は少ない） |
| `npc/kafras/` + `pre-re/kafras/` | 5 | 965 | **翻訳済み** |
| `npc/airports/` + `quests_airship` | 8 | 2,904 | 飛空艇（Ep.10。序盤導線ではない） |
| `instances/` `battleground/` `events/` | 19 | 3,361 | Pre-RE 序盤には不要 |
| `warps/` `mapflag/` `mobs/` | 194 | 146 | ほぼ文字列なし（Warp は無言） |

## 2. 導線ベースの優先順位（推奨バッチ）

「新規キャラで始めて 2 次転職・転生まで進める」流れで遭遇する順に並べた。数字は `mes` 行数（翻訳量の目安）。

### Batch 1: 最初の数時間で必ず会う（約 4,300 行）

| ファイル | `mes` | 内容 |
|---|---:|---|
| `npc/pre-re/jobs/novice/novice.txt` | 1,924 | 初心者修練場（new_1-1〜5-1）。初期地点なので最優先 |
| `npc/cities/prontera.txt` | 392 | プロンテラ住人 |
| `npc/cities/izlude.txt` | 265 | イズルード住人・**ビョルン島行きの船員** |
| `npc/cities/alberta.txt` | 181 | アルベルタ住人 |
| `npc/pre-re/guides/guides_{izlude,geffen,payon,morroc,alberta,aldebaran}.txt` | 約 430 | 主要 6 都市の案内員 |
| `npc/merchants/refine.txt` | 417 | **精錬 NPC**（各都市） |
| `npc/merchants/inn.txt` | 101 | 宿屋（HP/SP 回復） |
| `npc/merchants/renters.txt` | 98 | カート/ペコ/ファルコンのレンタル（商人は転職直後に必要） |
| `npc/merchants/novice_exchange.txt` | 215 | ノービス向け交換 |
| `npc/merchants/{old_pharmacist,alchemist,quivers}.txt` | 223 | 薬剤師・ポーション販売・矢筒 |
| `npc/other/bulletin_boards.txt` + `npc/pre-re/other/bulletin_boards.txt` | 377 | 各都市の掲示板（短文、露出が多い） |
| `npc/other/pvp.txt` | 186 | PvP 入口（要件の PvP 動線） |
| `npc/other/mail.txt` | 11 | 郵便 |

### Batch 2: 序盤〜中盤の街（約 4,500 行）

| ファイル | `mes` |
|---|---:|
| `npc/cities/geffen.txt` / `payon.txt` / `aldebaran.txt` | 794 / 672 / 886 |
| `npc/pre-re/quests/quests_morocc.txt`（Pre-RE のモロク街本体。`cities/morocc.txt` は Pre-RE では空） | 1,597 |
| `npc/cities/comodo.txt` / `yuno.txt` | 298 / 183 |
| `npc/pre-re/merchants/hair_style.txt` / `hair_dyer.txt`、`npc/merchants/{dye_maker,milk_trader,gemstone,elemental_trader,coin_exchange,enchan_arm,advanced_refiner}.txt` | 約 900 |
| 残りの `guides_*.txt`（Ep.10 以降の街含む） | 約 1,150 |

### Batch 3: 転職（約 10,800 行）

`npc/jobs/2-1/{knight,priest,wizard,blacksmith,hunter,assassin}.txt`（約 5,600）、`npc/jobs/2-2/{crusader,monk,sage,alchemist,rogue,bard,dancer}.txt`（約 5,000）、`npc/jobs/valkyrie.txt`（転生、183）。1 ファイル 1,000〜1,300 行と大きいので 1 ファイル 1 担当で並列。

### Batch 4: プラチナスキルクエスト（約 9,000 行）

`npc/quests/skills/novice_skills.txt`（339、応急手当・死んだふり）を先に、以下 1 次職 → 2 次職の順（thief 364 / merchant 503 / knight 368 / … / alchemist 1,631）。

### Batch 5: 序盤クエストとコンテンツ（約 9,000 行）

`npc/quests/quests_prontera.txt`（2,476。下水道入場含む）、`quests_alberta.txt`（1,751。タートル島・アマツ・崑崙・龍之城・アユタヤ行きの船）、`quests_geffen/payon/izlude/aldebaran/lutie/yuno.txt`（約 1,300）、`quests_comodo.txt`（1,775）、イズルード闘技場 `npc/other/arena/*`（1,248）。

### 後回し（導線外）

飛空艇（2,904）、結婚（530）、モンスターレース/ターボトラック/ポリン戦争/ビンゴ（約 2,600）、図書館の本 `books.txt`（2,829）、拡張職（テコン/ガンスリンガー/忍者/星/リンカー 約 2,500）、WoE 砦 NPC（1,250。動作自体は翻訳不要）、Ep.10 以降の街クエスト（約 60,000）、インスタンス/BG（Pre-RE 対象外）。

Batch 1〜5 の合計は約 38,000 行（全体の 21%）で、「通常プレイ導線」はこの範囲でほぼ日本語化できる。

## 3. 実装方針（既存方式の延長。追加するのは翻訳ファイルと補助ツールのみ）

### 3.1 配置と差し替え

- 翻訳版は上流のパスを鏡写しにして置く: `overlay-utf8/npc/custom/jp/<上流の npc/ 以下のパス>`。例: `npc/cities/prontera.txt` → `npc/custom/jp/cities/prontera.txt`、`npc/pre-re/jobs/novice/novice.txt` → `npc/custom/jp/pre-re/jobs/novice/novice.txt`（既存の `jobs/1-1/` と `kafras_pre-re.txt` は現行のままでよい）。
- 差し替えは `npc/scripts_custom.conf` の末尾ブロックに `delnpc: <上流パス>` / `npc: <翻訳版パス>` を対で追加。`delnpc` のパス文字列は上流の `scripts_*.conf` の表記と完全一致させる。
- **`MANIFEST.tsv`（上流パス TAB 翻訳版パス）を `overlay-utf8/npc/custom/jp/` に置き、`scripts_custom.conf` の JP ブロックはそこから生成する**（`tools/gen-jp-conf.py`）。手書きの対応漏れ・タイプミスを防ぐため。

### 3.2 検証の自動化（翻訳者の自己チェックをツール化）

- `scripts/check-jp-structure.sh`: MANIFEST の各行について、固定コミットの上流ファイル（GitHub raw を `~/.cache/rathena-<sha>/` にキャッシュ）と翻訳版を比較し、(a) 文字列リテラルを潰した構造 diff が「ヘッダ表示名と先頭コメント行」以外で一致、(b) `select(` のコロン数が一致、(c) `mes` 行数が一致、(d) BOM なし・LF・CP932 変換可、(e) 日本語直後の `\` エスケープなし、を機械判定する。
- 既存の `scripts/check-overlay.sh`（BOM/CP932/LF）に続けて実行し、両方 PASS を apply の前提にする。
- apply 前にローカル colima で `docker compose -f docker-compose.yml -f docker-compose.local.yml up --build` し、`status.sh` の `script error` / `npc_parse` が 0 であることを確認（NPC 構文エラーはそのファイルだけロード失敗になり、静かに機能が欠ける）。

### 3.3 翻訳ルール（これまでと同じ。`docs/JP_GLOSSARY.md` を新設して用語を固定）

- 文字列リテラルの中身だけ変更。関数名・ラベル・変数・`callfunc` 引数・イベント名・数値・`^RRGGBB`・`%` 書式・`//` コメントは不変。比較・識別子に使われる文字列は**同一ファイル内で両側を揃える場合のみ**翻訳（外部参照は `grep -rn` で確認）。
- ヘッダの表示名は `::ユニーク名` がある場合のみ翻訳。`doevent`/`donpcevent`/`getvariableofnpc` で参照される NPC 名は変更しない（Batch 1 候補は全て参照 0 を確認済み）。
- `select` の項目数維持、`mes` 行の増減なし、1 行全角 22 文字目安、日本語直後に `\` を置かない、CP932 に無い文字（U+301C 等）禁止。
- 用語集: 都市名・職業名・施設名・主要アイテム名・NPC 名のカタカナを固定（カプラ / プロンテラ / フェイヨン / モロク / アルデバラン …）。`getitemname()` で動的に出るアイテム名はサーバの `item_db` の英語名になる点は既知の制限（対処するなら `db/import/item_db.yml` の `Name` 上書きだが、`@item` やログにも影響するため別判断）。
- ライセンス: 全て独自訳。jRO 公式テキストの転載はしない。翻訳版ファイルは上流ヘッダを保持し GPL-3.0 派生物として扱う。

### 3.4 進め方

1. バッチ単位でファイルを担当分割（1 ファイル 1 担当、1,500 行超は分割せずそのまま）。
2. 用語集 → 翻訳 → `check-jp-structure.sh` → 用語レビュー → ローカル起動確認 → `terraform apply`（再配布は自動）。
3. 実機で英語のまま残っていた NPC 名を `docs/JP_BACKLOG.md` に記録し、次バッチの優先度に反映する。
4. `RATHENA_COMMIT` を上げるときは、翻訳済みファイルの上流差分（旧→新）を確認し、変わった箇所だけ再翻訳する。

### 3.5 NPC 以外で残っている日本語化

- Mob 名: 215 種のみ。Pre-RE 全 1,004 種への拡張は `db/import/mob_db.yml` への追記（データ作業。カタカナ表記の出所方針は要判断）。
- アイテム名・スキル名・マップ名・クエスト UI: クライアント側データ（クライアント側。現行は RO-Labo [../../client/README.md](../../client/README.md)「クライアント側の日本語」）。
- GM コマンドの応答: 英語のまま（`map_msg_eng_conf.txt` に追加すれば可能）。

## 4. 進捗（2026-09-23）

| Batch | 状態 | ファイル数 | 主な内容 | 結果ファイル |
|---|---|---|---|---|
| 1 | 完了（PASS） | 21 | 主要都市の住人・案内係・商人・掲示板・修練場 | `backups/jp-translation/batch-1-result-20260923-201353.txt` |
| 2 | 完了（PASS） | 33 | ゲフェン/フェイヨン/アルデバラン/コモド/ジュノー、モロク、美容師・染色屋・スロット付与、案内係 14 都市 | `backups/jp-translation/batch-2-result-20260923-213428.txt` |
| 3 | 完了（PASS） | 14 | 二次職転職クエスト 2-1/2-2 全 13 職 + 転生バルキリー | `backups/jp-translation/batch-3-result-20260923-221300.txt` |
| 4 | 完了（PASS） | 20 | プラチナスキルクエスト（`npc/quests/skills/*`） | `backups/jp-translation/batch-4-result-20260923-224345.txt` |
| 5 | 完了（PASS） | 18 | 初期都市クエスト 9（prontera/alberta/geffen/payon/izlude/aldebaran/lutie/comodo/yuno）+ イズルードアリーナ 9 | `backups/jp-translation/batch-5-result-20260923-232545.txt` |

合計: 117 ファイル / 42,128 mes（初期 11 ファイル 2,042 mes を含む）。最終状態のスナップショットは `backups/jp-translation/after-batch-5-20260923-232547/`。

各 Batch 開始前の状態は `backups/jp-translation/before-batch-N-*/`（`tools/jp-restore.sh` で復元可）。

### 4.1 Batch 2 で判明した rAthena の制約（重要）

`parse_variable()` の添字走査は文字列も 2 バイト文字も見ない生バイト走査のため、添字式 `var[...]` の中の文字列に
CP932 で 2 バイト目が `[`/`]` になる文字（ー ゼ ゾ ‐ ほか）があると map-server が起動時に SIGSEGV で落ちる
（再現はヒープ配置依存で不定）。`tools/jp_structure_check.py` の検査 1c で検出し、該当箇所は英語表記にする。
詳細は `docs/JP_TRANSLATION_RULES.md`。

## 5. 第 2 フェーズ（2026-09-24 開始）

| Phase | 内容 | 道具 |
|---|---|---|
| A | 117 ファイルの NPC 頭上表示名を `日本語#suffix::旧フル名` 形式で日本語化（exname 不変。分類 A=`::`あり/B=`::`追加/C=strnpcinfo(0|1) 依存で要判断/D=不可視・warp・shop は対象外） | `tools/jp_npc_names.py inventory/apply/check`、`docs/jp-npc-names.tsv` |
| B | 117 ファイルに残る英語表示文字列の機械監査と修正（意図的英語は `docs/jp-english-allowlist.tsv` で管理） | `tools/jp_english_audit.py` |
| C | 通常プレイ導線（修練場→プロンテラ→…→ジュノー、転職導線、日常 NPC）で未翻訳のファイルを追加 | `docs/JP_COVERAGE_PHASE2.md` の推奨リスト |

各 Phase の終了条件は Batch 1〜5 と同じ（構造検証 FAIL 0、CP932 OK、`gen-jp-conf.py --check` 差分なし、ローカル起動 13037 NPC・エラー 0、1c 添字走査 PASS）。開始前スナップショット: `backups/jp-translation/before-npc-name-phase2-20260924-004816/`。

### 5.1 第 2 フェーズ 完了（2026-09-24）

Phase A/B/C いずれも PASS。完了時点で MANIFEST 147 エントリ・mes 49,544 行、頭上名 1,047 体を日本語化（Phase A 704 + Phase C 343）。結果: `backups/jp-translation/phase2-{A,B,C}-result-*.txt`、最終スナップショット `backups/jp-translation/after-phase2-*/`。

同日 14:56 JST に独自 NPC「冒険者支援員」を追加のみで登録したことで、MANIFEST は 148 エントリ・mes 49,578 行に到達。NPC 総数は上流 13037 + 独自 NPC 6（サポート職員 1 + 冒険者支援員の修練場 5 面分 duplicate 5）で 13043。現行の数値は `docs/SPEC.md` §8 を参照。
