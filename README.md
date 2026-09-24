# RO-Labo

作成日: 2026-09-24
対象読者: 初見の SRE / 開発者、後続の別 AI。

## 1. これは何か

Windows の Chrome で動く roBrowserLegacy ベースのクライアントと、AWS 上の rAthena Pre-Renewal 検証サーバを組み合わせた、学習・検証目的のプロジェクトです。公式クライアント（Ragexe.exe）は使いません。日本語化と文字コード対応を独自に実装しています。

## 2. 全体 Architecture

```
Windows / Chrome
  roBrowserLegacy（client）
        | HTTP（資産） / WebSocket（ゲーム通信）
        v
  ro-glue（bridge, 127.0.0.1）
        | WS -> TCP 中継（バイト列透過）
        v
  AWS: rAthena Pre-Renewal（login/char/map）+ MariaDB
```

境界パラメータ、文字コード境界、責務表の詳細は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) を参照してください。

## 3. Client / Bridge / Server の役割

- **Client**（roBrowserLegacy）: 描画・入力・ログイン / キャラクター操作を行う Web クライアントです。ネットワーク文字列の CP932 変換も担います。
- **Bridge**（ro-glue）: 資産配信と WebSocket→TCP 中継を行うローカルプロセスです。パケットも文字コードも変換しない、バイト列透過の中継です。
- **Server**（rAthena Pre-Renewal）: 認証・キャラクター永続化・ゲームルール・NPC 日本語化を担います。クライアント作業からは変更しません（FREEZE）。

## 4. 外部依存

| 依存 | 内容 |
|---|---|
| jRO `data.grf` | ユーザー所有の正規インストール。読み取り専用で、リポジトリには含めません |
| AWS | サーバはこの上で稼働します（詳細は [server/docs/OPERATIONS.md](server/docs/OPERATIONS.md)） |
| rAthena | commit `e985006171d2eb320ee512a653f4c83aea3d81b6` |
| roBrowserLegacy | commit `e43b9b2bded117b945ebfd3d7604042546ca5354` |
| Node.js | 22（portable、`tools/node/`。当面このまま、Phase 3 で整理する） |

## 5. 現在の完成状況

> **2026-09-24 に AWS 上のサーバ環境は撤去済み**（`terraform destroy`、DLM スナップショットも削除）。以下はその時点の到達状況で、再構築すれば同じ状態に戻せます（手順は [server/README.md](server/README.md)）。

- サーバインフラ、rAthena 起動、ログイン、キャラクター作成 / 削除、ネットワーク文字コードは PASS（実装 + 日付入り検証記録あり）。
- NPC 台詞、Mob 名の日本語化は PARTIAL（対応ファイル数は docs/CURRENT_STATUS.md 参照）。
- 内蔵 UI の日本語化、Guild / Party 名、Electron 化、data.grf 自動検出は TODO。
- ネイティブ exe、Renewal / 3 次職、web-server はいずれも OUT OF SCOPE。
- 詳細・根拠・確認日は [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) を参照してください。

## 6. 起動方法

> サーバは撤去済みのため、現在は接続できません。先に [server/README.md](server/README.md)「構築手順」で再構築し、`client/robrowser/Config.local.js` の接続先を新しい IP に合わせてください。

サーバは稼働中であることを前提とします。クライアントの起動手順（glue の起動コマンド、アクセス URL）は [client/README.md](client/README.md) を参照してください。サーバ運用の入口は [server/README.md](server/README.md) です。

## 7. どこを直すか

| 直したいもの | 場所 |
|---|---|
| UI / 描画 / 入力 | `client/roBrowserLegacy-src/src/` |
| ネットワーク文字コード | 同 `src/Utils/CodepageManager.js` ほか、詳細は [client/docs/PATCHES.md](client/docs/PATCHES.md) |
| 配信・中継 | `client/ro-glue/server.mjs` |
| 接続先・PACKETVER | `client/robrowser/Config.local.js` |
| NPC 台詞・独自 NPC | [server/app/rathena/overlay-utf8/npc/custom/jp/](server/app/rathena/overlay-utf8/npc/custom/jp/) |
| 倍率・char / login 設定 | [server/app/rathena/conf/import/](server/app/rathena/conf/import/) |
| Mob 名 | [server/app/rathena/overlay-utf8/db/import/mob_db.yml](server/app/rathena/overlay-utf8/db/import/mob_db.yml) |
| アイテム・モンスターの性能、ドロップ表 | [server/app/rathena/overlay-utf8/db/import/](server/app/rathena/overlay-utf8/db/import/)（上流の db は無改変で、import 側の YAML で上書きする） |
| クライアントの再ビルド | [client/docs/BUILD.md](client/docs/BUILD.md) |
| インフラ | [server/terraform/](server/terraform/) |
| デプロイ | [server/docs/OPERATIONS.md](server/docs/OPERATIONS.md) |

`server/` はサーバ側リポジトリを丸ごと統合したもの。Terraform state・`.env`・バックアップは Git 管理外で運用者の Mac にのみ存在する。

## 8. 現在の構成

```
RO-Labo/
├─ README.md
├─ LICENSE / NOTICE.md
├─ docs/ARCHITECTURE.md, CURRENT_STATUS.md
├─ client/README.md docs/ ro-glue/ roBrowserLegacy-src/ robrowser/ clientdata/ scripts/
├─ notes/archive/*.md（HISTORICAL）
└─ server/README.md app/ terraform/ scripts/ tools/ docs/ backups/
```

Phase 3 では、Windows 側未追跡の `tools/node/` の扱いを整理する予定です。

## 9. ドキュメント一覧と SoT

| 領域 | SoT | 補助 |
|---|---|---|
| クライアント実装 | [client/README.md](client/README.md) | [client/docs/GLUE.md](client/docs/GLUE.md)、[PATCHES.md](client/docs/PATCHES.md)、[BUILD.md](client/docs/BUILD.md) |
| 全体アーキテクチャ・境界パラメータ・文字コード境界 | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | — |
| 現在地（PASS / PARTIAL / TODO / OUT OF SCOPE） | [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) | — |
| サーバ仕様・設定値 | [server/docs/SPEC.md](server/docs/SPEC.md) | — |
| サーバ運用・デプロイ | [server/docs/OPERATIONS.md](server/docs/OPERATIONS.md) | — |
| クライアント方式の設計判断 | [notes/archive/CLIENT_STRATEGY.md](notes/archive/CLIENT_STRATEGY.md)（HISTORICAL） | — |
| サーバ側の設計判断 | [server/docs/DESIGN.md](server/docs/DESIGN.md) §7 | [server/docs/CHANGELOG.md](server/docs/CHANGELOG.md)（経緯） |
| ライセンス | [LICENSE](LICENSE) | [NOTICE.md](NOTICE.md) |

## 10. 注意

- `client/roBrowserLegacy-src/AGENTS.md` などは上流 roBrowserLegacy 由来のファイルです。本プロジェクトの指示ではありません。
- `C:\Gravity\Ragnarok` はユーザー所有の正規インストールで、読み取り専用です。書き込みはしません。
- パスワードなどの秘密情報は、どの文書にも書きません。
- サーバはクライアント作業からは変更しません（FREEZE）。変更が必要に見える場合は Server-side Request として報告します。
