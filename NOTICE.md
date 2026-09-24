# NOTICE — ライセンスと帰属

最終更新: 2026-09-24

このリポジトリは GNU General Public License v3.0（[LICENSE](LICENSE)）の条件で配布します。理由は、GPL-3.0 で配布されている roBrowserLegacy の改変版ソースとそのビルド成果物を含むためです。本プロジェクト独自の部分（ro-glue、スクリプト、自作テクスチャ、文書）は GPL-3.0-or-later として提供します。

## 構成要素と出所

| 構成要素 | リポジトリ内の場所 | 出所 | ライセンス | 備考 |
|---|---|---|---|---|
| roBrowserLegacy（ソース） | `tools/roBrowserLegacy-src/` | [MrAntares/roBrowserLegacy](https://github.com/MrAntares/roBrowserLegacy) commit `e43b9b2bded117b945ebfd3d7604042546ca5354`。原作者 Vincent Thibault（roBrowser）と roBrowserLegacy の貢献者 | GPL-3.0（上流 `package.json` の `"license": "GNU GPL V3"`、同梱 `LICENSE`） | 上流から 8 ファイルを改変。一覧と目的は [client/docs/PATCHES.md](client/docs/PATCHES.md)。改変ファイル内への改変表示（GPL-3.0 第 5 条 a 項）は未追加で、Phase 2 以降で追記する |
| roBrowserLegacy（ビルド成果物） | `client/robrowser/`（`Online.js` ほか） | 上記ソースから本プロジェクトがビルド | GPL-3.0 | 対応するソースは上記ディレクトリ。再ビルド手順は [client/docs/BUILD.md](client/docs/BUILD.md) |
| roBrowserLegacy 同梱の第三者ライブラリ | `tools/roBrowserLegacy-src/src/Vendors/`（gl-matrix、html2canvas、iconv-lite、libgif、spark-md5、wasmoon / Lua 5.1、xmlparse） | 上流が同梱しているものをそのまま保持 | 各ファイル内の著作権・ライセンス表示に従う | 本プロジェクトでは無改変 |
| ro-glue | `tools/ro-glue/` | 本プロジェクト | GPL-3.0-or-later（`package.json`） | GRF エントリの DES 復号に roBrowserLegacy の `src/Loaders/GameFileDecrypt.js`（GPL-3.0）を import する |
| ws | npm 依存（`node_modules/`、リポジトリには含めない） | [websockets/ws](https://github.com/websockets/ws) | MIT | 利用者が `npm install` で取得する |
| 自作ログイン UI テクスチャ | `client/clientdata/data/texture/유저인터페이스/login_interface/` | 本プロジェクト（`tools/scripts/make-login-overlay.ps1` で描画） | GPL-3.0-or-later | jRO の `bgi_temp.bmp` を分割した背景タイル `t_*.bmp` は再配布しないためリポジトリに含めない（`.gitignore`） |
| スクリプト・文書 | `tools/scripts/`、`docs/`、`notes/`、各 README | 本プロジェクト | GPL-3.0-or-later | |
| jRO クライアント資産（`data.grf`、`Ragexe.exe` 等） | 含まない | Gravity Co., Ltd. / ガンホー・オンライン・エンターテイメント | プロプライエタリ | 利用者が所有する正規インストール（例: `C:\Gravity\Ragnarok`）を読み取り専用で参照するだけで、複製・再配布・改変はしない |
| rAthena（サーバ側。Phase 2 で `server/` として統合予定） | 現時点では含まない | [rathena/rathena](https://github.com/rathena/rathena) commit `e985006171d2eb320ee512a653f4c83aea3d81b6` | GPL-3.0 | 本体は無改変。NPC スクリプトの日本語訳は rAthena の派生物として GPL-3.0 |

## GPL-3.0 上の遵守事項と現状

| 要件 | 現状 |
|---|---|
| ライセンス全文の同梱 | `LICENSE`（上流と同一の GPLv3 本文） |
| 対応ソースコードの提供 | 改変版ソースを `tools/roBrowserLegacy-src/` に同梱 |
| 改変ファイルへの改変表示と日付（第 5 条 a 項） | **未対応**。一覧は `client/docs/PATCHES.md` に記録済み。ソースへのヘッダ追記はコード変更を伴うため Phase 2 以降で行う |
| 第三者ライブラリの表示保持 | 上流のファイルを無改変で保持 |

## やらないこと

- jRO / kRO のクライアント、GRF、パッチファイルの複製・再配布。
- 保護付き実行ファイル（Themida / GameGuard）の解析・回避。
- 第三者が運営する RO サーバへの接続。
