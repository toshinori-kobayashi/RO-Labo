# RO-Labo 現在地

作成日: 2026-09-24
対象読者: 初見の SRE / 開発者、後続の別 AI。

> **2026-09-24 に AWS 環境を撤去済み。** サーバ側の行はいずれも撤去直前の最終状態の記録です。再構築（[../server/README.md](../server/README.md)）後に再検証してください。

## 凡例

状態:

- **PASS**: 実装済みで、動作を確認した記録がある。
- **PARTIAL**: 一部のみ実装・確認できている。
- **TODO**: 未実装、または実装はあるが未検証。
- **OUT OF SCOPE**: 対応しない方針として決定済み。
- **未確認**: 実装の有無に関わらず、検証記録が無い。

根拠の強さ:

- **強**: 現行のコード/設定と、日付入りの検証記録の両方がある。
- **中**: どちらか一方のみがある。
- **弱**: 過去メモの記述のみで、現行コード/設定や日付入りの検証記録が無い。
- **—**: 方針決定・未着手のため強さの評価対象外。

## 現在地一覧

| 項目 | 状態 | 根拠 | 根拠の強さ | 最終確認日 |
|---|---|---|---|---|
| Infrastructure（Terraform、SSM デプロイ、DLM、CloudWatch） | 撤去済み（2026-09-24。撤去前は PASS） | [server/docs/SPEC.md](../server/docs/SPEC.md) §4、CHANGELOG（最終デプロイ 2026-09-24 14:56 JST） | 強 | 2026-09-24 |
| rAthena Pre-Renewal（e985006 / PACKETVER 20211103） | PASS | `app/config.env`、起動ログ「Done loading '13043' NPCs」 | 強 | 2026-09-24 |
| Login（Chrome → glue → login/char/map） | PASS | クライアント E2E 2026-09-23、EC2 内 probe 2026-09-24、実クライアント 2026-09-24 | 強 | 2026-09-24 |
| Character Create（日本語名） | PASS | 「ユンヌ」作成 2026-09-23。「シアレス」は文字コード修正前の作成で UTF-8 保存のため試験対象外。日本語名の可否・文字数制限はサーバ側設定による（[server/docs/SPEC.md](../server/docs/SPEC.md) 参照） | 強 | 2026-09-23 |
| Character Delete（生年月日方式） | PASS | 実クライアントで「ユンヌ」削除 2026-09-24、probe で result 1、`CharEngine.js` の改変を実装で確認 | 強 | 2026-09-24 |
| Network CP932（送受信） | PASS | クライアント側 4 ファイルの改変と `Online.js` への反映を確認、MOTD・日本語キャラ名の往復を 2026-09-23 に観測 | 強 | 2026-09-23 |
| Japanese Chat | PASS（クライアント側観測のみ） | クライアント側では 2026-09-23 に日本語チャットの表示確認の記録があるが、サーバ側 chatlog の証跡は無い（`log_chat` 無効で 0 行）。ギルド / パーティチャットは未確認 | 中 | 2026-09-23（クライアント側のみ） |
| Japanese NPC dialogue | PARTIAL | 148/527 ファイル、頭上表示名 1,099/1,108 体（[server/docs/SPEC.md](../server/docs/SPEC.md) §8） | 強 | 2026-09-24 |
| Japanese Mob names | PARTIAL | `mob_db.yml` 215 件、`override_mob_names: 2` | 強 | 2026-09-24 |
| Japanese Skills（名前 / 説明） | PASS / PARTIAL | `DBManager.js` の skill-jp 実装を確認。lub に無いスキルの説明は `...`、スキルツリー表示は 7 文字で切れる。日付入りの試験表は無い | 中 | 記録なし |
| Japanese Item names（インベントリ表示） | 未確認 | GRF の `idnum2itemdisplaynametable.txt` は読めている（2026-09-23）が、実インベントリでの表示記録は無い。NPC 台詞中の `getitemname()` はサーバ側で英語のまま | 弱 | 2026-09-23（テーブル読み取りのみ） |
| MOTD 日本語 | PASS | 2026-09-23 観測（文字コード修正後） | 中 | 2026-09-23 |
| Login UI overlay（自作 19 ファイル、うち 7 をリポジトリにコミット） | PASS | `make-login-overlay.ps1` による生成、2026-09-23 の E2E で確認 | 強 | 2026-09-23 |
| Training Skip NPC（冒険者支援員） | PASS | ローカル + EC2 probe で 6 職・辞退・キャンセル・再訪拒否を確認、2026-09-24 14:56 JST 反映分で最終確認 | 強 | 2026-09-24 |
| Support NPC（サポート職員） | PASS | 初期構築から稼働（[server/docs/SPEC.md](../server/docs/SPEC.md) §9.1）。クライアントから会話を確認した記録は無い | 中 | 記録なし |
| Client built-in UI Japanese（職業名・メニュー・ステータス欄） | TODO | `Config.local.js` の `loadLua: false` を実ファイルで確認。[client/README.md](../client/README.md) の未対応節を参照 | 強 | 2026-09-24（本書作成時に実ファイルで再確認） |
| Guild / Party name input（日本語） | TODO（未検証） | 検証記録なし（[server/docs/SPEC.md](../server/docs/SPEC.md) §12、CLIENT_HANDOFF チェックリスト） | — | 記録なし |
| data.grf auto detection | TODO | `--grf` はコマンドライン引数で指定する。`client/ro-glue/server.mjs` はコード上 `--static` のみを必須引数としてチェックしており（未指定だと起動時エラー）、`--grf` 自体に必須チェックは無い。ただし指定しなければ GRF 由来の資産は配信されず、自動検出ロジックも無い | 中 | 2026-09-24（実ファイルで再確認） |
| 起動の 1 コマンド化 / start-glue.ps1 | TODO | 未実装（Phase 3 で予定） | 強 | — |
| Electron packaging（RO-PreRE.exe） | TODO | 未着手。上流 `applications/electron` はサンプル参照のみ | 強 | — |
| Native Ragexe（kRO RagexeRE / jRO Ragexe.exe） | OUT OF SCOPE | 方式判断（[notes/archive/CLIENT_STRATEGY.md](../notes/archive/CLIENT_STRATEGY.md)、HISTORICAL）。jRO exe は保護付きの別系列、kRO 2021-11-03 は正規入手不可 | — | — |
| Renewal / 3 次職 | OUT OF SCOPE | `Config.local.js` の `renewal: false` を実ファイルで確認。サーバは `--enable-prere=yes` | 強 | 2026-09-24 |
| web-server 8888 / ギルドエンブレム | OUT OF SCOPE | 設計判断（[server/docs/DESIGN.md](../server/docs/DESIGN.md) §7） | — | — |
| Security（公開範囲、秘密情報、IP の整理） | TODO（後工程） | 本リポジトリは public。サーバ側資料（`server/`）を統合する前に公開範囲の判断が必要。接続先 IP や識別子の整理は未着手 | — | 2026-09-24 |

## 次に検証すべきこと

- Guild / Party 名の日本語入力・表示。
- インベントリ上のアイテム名表示（日本語で出ているかどうか）。
- 日本語チャットのサーバ側記録方法（`log_chat` を有効にするかどうかの判断を含む）。

## 更新ルール

状態を変えるときは、根拠と最終確認日を必ず一緒に書き換えてください。根拠が「記録なし」のまま状態だけを変えないでください。
