> **HISTORICAL（2026-09-24）** — 2026-09-23 時点の方式比較と採用判断の記録です。判断（roBrowserLegacy + 手元 jRO data.grf、ネイティブ exe 不採用）は現在も有効ですが、§5〜§7 の構成・E2E 結果・Blocker は当時のものです。現行仕様は [client/README.md](../../client/README.md)、現在地は [docs/CURRENT_STATUS.md](../../docs/CURRENT_STATUS.md)。

# CLIENT_STRATEGY

作成日: 2026-09-23
目的: rAthena Pre-Renewal サーバ（54.65.172.5, PACKETVER 20211103, **FREEZE**）に対して
「サーバを変えず、合法的な手元資産 + OSS だけで」接続できる Windows クライアント方式を決める。

前提（変更不可）
- サーバ側: Terraform / AWS / rAthena 設定 / PACKETVER / サーバコード 一切変更しない（Server Changes = NONE）
- jRO `Ragexe.exe` は使わない（別プロトコル系列、Themida/WinLicense + GameGuard。保護解除は禁止）
- `C:\Gravity\Ragnarok` は読み取り専用の公式資産ソース。変更禁止
- 非公式ミラー / crack・unpack 済み exe / 第三者 GRF の取得禁止。保護回避が必要な方式は不採用

---

## 1. 結論（Recommendation）

**方式 B+C を採用: OSS クライアント roBrowserLegacy + jRO 公式 `data.grf`（手元・読み取り専用）**

- サーバは一切変更しない。PACKETVER 20211103 / renewal=false はクライアント側設定で一致させる。
- クライアント本体は OSS（GPL-3.0）の roBrowserLegacy Web ビルドを Chrome で実行。
- ゲーム資産（テクスチャ・スプライト・マップ・テーブル）は手元の jRO `data.grf` から **ローカル配信のみ**（再配布しない）。
- TCP 接続はローカルの小さな Node 中継（自作 `ro-glue`、宛先を 54.65.172.5 の 3 ポートに固定）経由。
- 保護回避は不要。exe の改変・unpack・GameGuard 停止はどれも行っていない。

**「jRO exe が使えない → rAthena を捨てる」にはならない。** サーバ変更要求（Server-side Request）も無し。

---

## 2. 比較表（Compared Options）

| 観点 | A. Native RagexeRE 2021-11-03 | B. OSS クライアント（roBrowserLegacy） | C. jRO data.grf 再利用（B と併用） |
|---|---|---|---|
| PACKETVER 20211103 | ○（本来の対象 exe） | ○ `PacketVersions.js` に 20211103 定義、`CHARACTER_INFO` int64 分岐あり | ―（データのみ。パケット非依存） |
| rAthena 互換 | ○ | ○（rAthena/Hercules 向け OSS） | ― |
| Pre-Renewal | ○（clientinfo/servertype 次第） | ○ `renewal: false` | ○ Pre-RE マップ/スプライトは同梱 |
| Windows | ○ | ○（Chrome 153 で動作確認） | ○ |
| 日本語表示 | ○（jRO data 併用時） | △ `langtype:2 → shift-jis` デコード実装あり。実表示は E2E 後半で確認 | ○ 日本語テーブル（msgstringtable 等）同梱 |
| 日本語 IME | ○ | ○（ブラウザ標準 `<input>`、OS IME がそのまま使える） | ― |
| jRO data.grf 再利用 | △ exe 側は kRO 依存ファイルを要求 | ○ GRF 0x300 + 標準 DES フラグを読める | ○ 標準 GRF 0x300 / zlib / EUC-KR パス |
| 公式・OSS のみで構成可能 | **×** 2021-11-03 exe は公式配布終了。入手経路が非公式ミラーのみ | ○ GitHub 公式リリース + nodejs.org | ○ 手元の正規インストール |
| 保護回避不要 | ○（入手できれば） | ○ | ○（GRF の DES はファイル形式仕様。exe 保護とは無関係） |
| E2E までの難易度 | **入手不能で開始不可** | 低〜中（起動→サーバ選択→ログイン画面まで PASS 済み） | 低（kRO 依存 UI 画像 19 点のみ自作で補完） |
| 判定 | **不採用**（入手経路が禁止事項に抵触） | **採用** | **採用（B のデータソース）** |

### A を不採用にした根拠
- kRO 公式 (ro.gnjoy.com) が配布しているのは現行 2026 年版フルクライアントのみ。2021-11-03 RagexeRE は公式配布終了。
- 現行 kRO exe は PACKETVER が新しく、FREEZE 中のサーバ (20211103) と不一致。サーバ変更なしでは接続不可。
- rAthena フォーラム「Client Releases」等は第三者による再配布 = 「非公式ミラーから公式クライアントを取得」に該当 → 禁止。

### 他の OSS 候補（README / ソース確認済み。名前で判断していない）
| 候補 | ライセンス | 判定 | 理由 |
|---|---|---|---|
| Korangar (vE5li) | MIT | 不採用 | Rust nightly + Vulkan SDK/Slang が必要 = 「大量の SDK 導入」停止条件に該当。PACKETVER 追従も要確認 |
| OpenMidgard | GPL-3 | 不採用 | 2008 年プロトコル（packet_ver 23）。20211103 非対応 |
| Lifthrasir | GPL-3 | 不採用 | Aesir 系ローダのみ。ゲームクライアントではない |
| lenaxia/rathena-client | ― | 不採用 | Go のプロトコルライブラリ。UI/描画なし |
| roBrowserLegacy-RemoteClient-JS | ライセンス表記なし | 不採用 | 「0x200/0x300 は DES 無しのみ」対応、ライセンス不明 → 自作 glue で代替 |

---

## 3. 採用 OSS（OSS）

| 項目 | 内容 |
|---|---|
| 方式 | roBrowserLegacy（Web ビルド）を Chrome で実行 |
| URL | https://github.com/MrAntares/roBrowserLegacy |
| version / tag / commit | nightly release `release-dist-web.zip`（build 2026-09-23 07:19:44）/ ソース commit `e43b9b2bded117b945ebfd3d7604042546ca5354` |
| license | GPL-3.0 |
| 対応 PACKETVER | `src/Network/PacketVersions.js` に 20211103 を含む多数。`renewal` フラグで Pre-RE/RE 切替 |
| jRO 資産互換性 | GRF 0x200/0x300、標準 DES フラグ (0x02/0x04) 対応。jRO data.grf は 0x300 "Event Horizon" + zlib テーブル + EUC-KR パス → 全 252,721 エントリをインデックス化できた |
| 日本語対応 | `CodepageManager.detectEncodingByLangtype(2)` → `'shift-jis'`。入力は HTML `<input>` なので OS IME 利用可 |
| ダウンロード検証 | `robrowser-release-dist-web.zip` sha256 `87eb7c00…8482f027`（GitHub release digest 一致）、ソース zip sha256 `3cdd33dd…04f1f0` |
| 付随 | Node.js v22.23.2 win-x64 zip（MIT, nodejs.org SHASUMS256 一致 `1177b413…c99f97`）、npm `ws` ^8（MIT） |

### 自作部分（ro-glue, `C:\RO-Lab\tools\ro-glue\server.mjs`, GPL-3.0-or-later）
1. 静的配信: `C:\RO-Lab\client\robrowser\`（dist の作業コピー + `Config.local.js`）
2. 資産配信 `/client/<path>`: loose 上書き (`C:\RO-Lab\client\clientdata`, `C:\Gravity\Ragnarok`) → `data.grf`。
   - DES 復号は roBrowserLegacy 同梱の `src/Loaders/GameFileDecrypt.js` を import（GPL、そのまま利用）
   - パス照合: ブラウザは GRF 名を windows-1252 として送るので、生バイト(latin1) と EUC-KR 復号の両方のキーで照合
   - `POST filter=` 正規表現検索、`POST batch` にも対応
3. WebSocket→TCP 中継 `ws://127.0.0.1:8000/<ip>:<port>`: 許可先 `54.65.172.5:{6900,6121,5121}` のみ。他は 403。
4. `remoteClient` は必ずローカル (`http://127.0.0.1:8000/client/`)。既定の `https://grf.robrowser.com/` には一切アクセスしない。

---

## 4. jRO 資産の調査結果（jRO Assets）

対象: `C:\Gravity\Ragnarok\data.grf`（4,569,872,560 B, 2025-04-27）読み取りのみ。`event.grf` (0x103) は未使用。

| 項目 | 結果 |
|---|---|
| GRF ヘッダ | 署名 `Event Horizon`、version **0x300**（64bit テーブルオフセット @30、ファイル数 @38、テーブル前に Int32 1 個） |
| ファイルテーブル | zlib 圧縮（標準）。エントリ = name\0 + pack/aligned/real (u32×3) + type u8 + offset u64 |
| エントリ数 | 252,721（type&0x01） |
| 暗号化フラグ | 43,604 エントリが 0x02/0x04（標準 Gravity DES）。roBrowser 実装で復号できた（win_login.bmp, poring.spr/act 等で確認） |
| ファイル名エンコード | EUC-KR（kRO 形式ディレクトリ名 `유저인터페이스`, `몬스터` など）。glue で両エンコードのキーを保持 |
| 日本語テーブル | `msgstringtable.txt`(86 KB) `idnum2itemdisplaynametable.txt`(425 KB) 等 GRF 内。`System\iteminfo.lub`(890 KB) はルーズ |
| Lua/Lub | `System\LuaFiles514\` はルーズ 2 ファイルのみ。その他は GRF 内 luafiles514（roBrowser は `loadLua:false` で未使用） |
| マップ | `prontera.gat/gnd/rsw` 取得 OK（2.4 MB / 3.9 MB / 533 KB） |
| **不足（kRO 依存）** | roBrowser が PACKETVER≥20181114 で要求する kRO 新ログイン UI: `login_interface/bg_login.tga`, `bt_start_{normal,over,press}.bmp`, `bt_join_{normal,over,press}.bmp`, 背景タイル `t_배경1-1..3-4.bmp`（計 19 ファイル）。jRO は旧式 `win_login.bmp` 系のみ保持 |
| 対処 | 上記 19 ファイルを **自作** して loose 上書き（`tools\scripts\make-login-overlay.ps1`）。ボタン/パネルは System.Drawing で描画、背景タイルは手元 `bgi_temp.bmp`(1280×720) を 4×3 分割（ローカル利用のみ、再配布しない） |
| 変換の必要性 | GRF 変換・再パックは不要。ファイル形式は全て標準 |
| 再配布 | 行わない。glue は 127.0.0.1 のみ listen |

---

## 5. プロトタイプ構成（Prototype）

```
C:\RO-Lab\
  tools\
    node\                       Node v22.23.2 portable
    roBrowserLegacy-dist\       release-dist-web.zip 展開（未改変）
    roBrowserLegacy-src\        commit e43b9b2 ソース（GameFileDecrypt.js を import するため）
    ro-glue\                    自作 glue（server.mjs, package.json, node_modules/ws）
    scripts\grf-inspect.ps1     GRF 0x200/0x300 読み取り専用インスペクタ
    scripts\make-login-overlay.ps1  kRO 依存 UI 19 ファイルの自作生成
    downloads\                  取得 zip（SHA256 検証済み）
  client\
    robrowser\                  dist の作業コピー + Config.local.js
    clientdata\data\clientinfo.xml            段階1 clientinfo（loose 上書き用）
    clientdata\data\texture\유저인터페이스\  自作 UI オーバーレイ 19 ファイル
    data\clientinfo.xml, sclientinfo.xml      段階1（ネイティブ exe 用に作成したもの。参考保管）
  original\                     空（jRO 資産は C:\Gravity をそのまま参照、コピーしない）
  notes\glue-server.log         glue ログ
```

起動手順:
```powershell
cd C:\RO-Lab\tools\ro-glue
C:\RO-Lab\tools\node\node.exe server.mjs --port 8000 `
  --static "C:\RO-Lab\client\robrowser" `
  --grf "C:\Gravity\Ragnarok\data.grf" `
  --loose "C:\RO-Lab\client\clientdata" --loose "C:\Gravity\Ragnarok" `
  --allow "54.65.172.5:6900,54.65.172.5:6121,54.65.172.5:5121" `
  --decrypt "C:\RO-Lab\tools\roBrowserLegacy-src\src\Loaders\GameFileDecrypt.js"
# Chrome で http://127.0.0.1:8000/api.html?app=ONLINE
```

`Config.local.js` 要点: `address 54.65.172.5 / port 6900 / version 55 / langtype 2 / packetver 20211103 / renewal false /
packetKeys false / socketProxy ws://127.0.0.1:8000/ / remoteClient http://127.0.0.1:8000/client/ / skipIntro true / skipServerList false`

---

## 6. E2E 結果（2026-09-23）

| Phase | 内容 | 結果 | 証跡 |
|---|---|---|---|
| 1 | クライアント起動 | **PASS** | WebGL キャンバス描画、jRO 背景 `bgi_temp.bmp` 表示 |
| 2 | サーバ選択に `RO PreRE` | **PASS** | Service Select に 1 件表示、OK で遷移 |
| 3 | ログイン画面 | **PASS** | WinLoginV2（自作オーバーレイ UI）表示。ID/PW 入力欄・Login ボタン |
| 3' | login-server 6900 到達 | TCP レベル PASS（3 ポートとも connect OK） | クライアント経由は認証情報待ち |
| 4 | ログイン認証 | **未実施** | `player01` のパスワード未設定 → ユーザーに設定依頼 |
| 5 | char-server 遷移 | 未実施 | |
| 6 | キャラ作成/選択 | 未実施 | |
| 7 | map-server 遷移 | 未実施 | |
| 8 | ゲーム画面 | 未実施 | |

資産配信統計（ログイン画面まで）: hits 53 / misses 0（自作オーバーレイ適用後）。

---

## 7. Blockers / 判断事項

1. **認証情報**: `player01` のパスワードが未設定（README: `RO_PASSWORD='...' scripts/set-password.sh player01`）。
   ログ・ファイルから探索はしていない。ユーザーに設定依頼 → 受領後 Phase 4 以降を実施。
2. **GRF DES 復号の扱い**（判断）: jRO data.grf の 43,604 エントリは GRF 形式仕様の DES フラグ付き。
   これは全 GRF ツール/roBrowser が実装するファイル形式互換機能であり、exe の Themida/GameGuard 回避とは別物と判断して実施。
   「保護解除」と見なす運用であれば、該当エントリを使わない構成に戻す（UI 画像・スプライト・610 マップが読めなくなる）。
3. **kRO 依存 UI 19 ファイル**: 自作で補完済み。見栄えは簡素。jRO 風にしたい場合は旧 `WinLogin`（win_login.bmp 系）を使うよう
   roBrowser 側の UI バージョン表を変える案があるが、12 MB バンドルの改変になるため今回は見送り。
4. **Node.js 導入**（判断）: portable zip 展開のみ（管理者権限不要、PATH 変更なし）。「大量の SDK 導入」には該当しないと判断。
5. 未確認: 日本語チャット表示/IME 入力の実挙動（Phase 8 到達後）、`loading*.jpg` の有無（無ければ黒背景で進むだけ）。

---

## 8. Server Changes

**NONE.** Server-side Request も無し。
