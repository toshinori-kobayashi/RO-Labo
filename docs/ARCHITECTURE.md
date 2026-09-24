# RO-Labo アーキテクチャ

作成日: 2026-09-24
対象読者: 初見の SRE / 開発者、後続の別 AI。

全体像を 1 枚に集約した文書です。個別実装は [client/README.md](../client/README.md) と [client/docs/](../client/docs/) 配下、サーバ実装は `server/docs/SPEC.md`（統合予定パス。Phase 2 で `server/` として統合されるまでは、サーバ担当のローカルリポジトリ `ro-server/` に同名のパス構成で存在する）を参照してください。

## 1. 全体図

```
Windows / Chrome
  roBrowserLegacy（client, WebGL, GPL-3.0）
        |
        | HTTP  GET /client/<path>            資産（GRF / loose）
        | WS    /<接続先 ip>:<接続先 port>     ゲーム通信
        v
  ro-glue（bridge, 127.0.0.1 のみで待受）
        |  静的配信 + GRF / loose 資産配信
        |  WS -> TCP 中継（許可リストのみ、バイト列透過）
        v
  AWS ap-northeast-1 EC2（Docker Compose）
        login-server --+
        char-server  --+-- rAthena Pre-Renewal（本体無改変）
        map-server   --+
        |
        v
  MariaDB（utf8mb4、rAthena からの接続は cp932）
```

jRO `data.grf` はユーザー所有・読み取り専用でクライアント PC 上にあり、ro-glue がローカルにのみ配信します。127.0.0.1 の外へは出ません。

## 2. 境界パラメータ

クライアントとサーバの接続を成立させている値です。実装上の唯一の正はコード（`client/robrowser/Config.local.js` と glue の `--allow`）で、この表はその写しです。値を変えるときはコードを直してからこの表を更新してください。

| 項目 | 値 | 出典 |
|---|---|---|
| login ポート | 6900 | Config.local.js `port` |
| char ポート | 6121 | サーバ通知（glue の許可リストに含める） |
| map ポート | 5121 | サーバ通知（同上） |
| PACKETVER | 20211103 | Config.local.js `packetver` |
| langtype | 2（日本） | Config.local.js `langtype` |
| renewal | false（Pre-Renewal） | Config.local.js `renewal` |
| packetKeys | false | Config.local.js `packetKeys` |
| version（クライアント version 検査） | 55 | Config.local.js `version` |
| ネットワーク文字コード | CP932 | 本書 §5 |
| 接続先ホスト（EIP） | client/README.md 参照 | — |

## 3. 責務（Client / Bridge / Server）

**ro-glue はパケットの中身も文字コードも意味的に変換しない、バイト列透過の中継です。** WS→TCP のリレーはサーバから届いたバイト列をそのまま `ws.send(d)` し、クライアントから届いたバイト列をそのまま `tcp.write(b)` するだけです（`tools/ro-glue/server.mjs`）。GRF / loose の資産配信もファイルの中身を書き換えません。

| 責務 | 担当 | 根拠（実ファイル） |
|---|---|---|
| 描画、UI、入力、IME | Client | `tools/roBrowserLegacy-src/src/UI/`, `src/Renderer/` |
| ネットワーク文字列の CP932 encode/decode | Client | `src/Utils/CodepageManager.js`、`BinaryReader.js`、`BinaryWriter.js` |
| スキル名・説明の日本語表示（lub 文字列抽出） | Client | `src/DB/DBManager.js`（skill-jp） |
| 削除確認コード入力 UI（YYYYMMDD → YYMMDD） | Client | `src/Engine/CharEngine.js`、`src/UI/Components/CharSelect/CharSelectCommon.js` |
| 接続先・PACKETVER・langtype の宣言 | Client | `client/robrowser/Config.local.js` `servers[]` |
| 静的配信、GRF / loose 資産配信 | Bridge | `tools/ro-glue/server.mjs`（`/client/<path>`） |
| WS → TCP 中継（許可リストのみ、バイト列透過） | Bridge | `tools/ro-glue/server.mjs`（`server.on('upgrade', ...)`、`allowSet` で 403 判定） |
| 認証、キャラクター永続化、削除の照合（birthdate） | Server | login/char-server、`char_conf` |
| ゲームルール、EXP / ドロップ倍率、モンスター・アイテム性能 | Server | `battle_conf`、db（値は `server/docs/SPEC.md`） |
| NPC 台詞・頭上名・独自 NPC | Server | `overlay-utf8/npc`（統合予定パス `server/app/rathena/overlay-utf8/npc/`） |
| Mob 表示名、MOTD、サーバメッセージ | Server | `mob_db.yml`、`motd`、`map_msg` |
| インフラ、デプロイ、バックアップ | Server | Terraform / SSM / DLM（統合予定パス `server/terraform/`） |

## 4. 通信境界

- HTTP は資産配信のみです: `GET /client/<path>`（loose → GRF の順で解決、なければ 404）、`POST /client/`（filter 検索）、`POST /client/batch`（一括取得）、`GET /__status`（状態確認）。
- WebSocket は `ws://127.0.0.1:<port>/<接続先 ip>:<接続先 port>` の形式で、1 接続 = TCP 1 本です。URL のホスト:ポートが glue の許可リスト（`--allow`）に無ければ `403 Forbidden` で切断されます（`tools/ro-glue/server.mjs` の `server.on('upgrade', ...)`）。
- char / map への遷移は、サーバがクライアントへ次の接続先（ip:port）を通知し、クライアントがその接続先で glue に新しい WebSocket を張り直すことで行われます。glue 側は接続先ごとに新しい TCP を都度張ります。

## 5. 文字コード境界

| 層 | 文字コード | 実装箇所 |
|---|---|---|
| GRF 内のファイル名 | windows-1252（`userCharset`） | Client `DBManager.js` |
| テキストテーブル（msgstringtable 等） | shift-jis（langtype 2 由来。iconv-lite 上は CP932 と同一の変換表） | Client `DBManager.js`（`userCharpage`） |
| ネットワーク送受信 | CP932（`networkCharset`） | Client `CodepageManager.js` / `BinaryReader.js` / `BinaryWriter.js`。`decodeNetwork` は UTF-8 を先に試し、不正なら networkCharset にフォールバックする |
| glue（資産配信・WS 中継） | 無変換（バイト列透過） | `tools/ro-glue/server.mjs` |
| DB | テーブルは utf8mb4、rAthena からの接続は cp932 | サーバ側 MariaDB / `inter_conf.txt.tmpl` |

送信時の正規化ルール（U+301C→U+FF5E 等）や、固定長フィールドを文字境界で切り詰める実装の詳細は [client/README.md](../client/README.md) を参照してください。

## 6. 資産の責務

| 資産 | 所有 | 扱い |
|---|---|---|
| jRO `data.grf` | ユーザー所有 | 読み取り専用、非同梱、127.0.0.1 の外へ出さない |
| loose overlay（ログイン UI 等） | 本プロジェクト | `client/clientdata/` 配下、リポジトリ管理 |
| roBrowserLegacy ビルド成果物 | 上流 + 本プロジェクトの改変 | GPL-3.0、`client/robrowser/` 配下 |
| サーバ NPC 翻訳 | 本プロジェクト | リポジトリ管理（統合予定パス `server/app/rathena/overlay-utf8/npc/custom/jp/`） |

## 7. 永続化境界

- クライアント: ゲームデータを永続保存しません（`saveFiles: false`、削除確認コードもクライアントには保存しません）。
- glue: キャッシュを持ちません。リクエストのたびに GRF / loose からファイルを読みます。ディスクへの書き込みはしません。
- サーバ: MariaDB がアカウント・キャラクター等を永続化します。EBS 上に配置し、日次 mysqldump と DLM スナップショットでバックアップします（詳細は `server/docs/OPERATIONS.md` 統合予定パス）。

## 8. デプロイ境界

- クライアント: 手元ビルド（[client/docs/BUILD.md](../client/docs/BUILD.md)）→ 成果物を `client/robrowser/` へコピー。
- glue: 手元で `node server.mjs` を起動するだけです（[client/docs/GLUE.md](../client/docs/GLUE.md)）。
- サーバ: `terraform apply` → アプリ一式を S3 へアップロード → SSM Association 経由で EC2 に配布 → EC2 上で `docker compose build` して再起動します（統合予定パス `server/docs/OPERATIONS.md`）。
