> **ARCHIVED / HISTORICAL（2026-09-24）** — この文書は現在の仕様ではありません。作成時点（2026-09-23）の調査・作業記録として残しています。
> 現行仕様: クライアントは [client/README.md](../../client/README.md)、全体構成は [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)、現在地は [docs/CURRENT_STATUS.md](../../docs/CURRENT_STATUS.md)。2026-09-24 に `notes/archive/` へ移動済み。

# RO-Lab クライアント実装・仕様まとめ

作成日: 2026-09-23  
対象読者: 後続の作業者 / ChatGPT プロジェクトの情報源  
この文書の位置づけ: **Windows クライアント側の現行仕様と実装の SoT**。サーバ構築・Terraform・rAthena 運用は対象外。

関連文書:

| 文書 | 内容 | 注意 |
|---|---|---|
| `C:\RO-Lab\RO\RO\ro-server\CLIENT_HANDOFF.md` | サーバ側から見たクライアント接続仕様（SoT） | ネイティブ RagexeRE 想定の記述が多い |
| `C:\RO-Lab\RO\RO\ro-server\README.md` | サーバ運用。PACKETVER、アカウント発行手順 | パスワードは書かない |
| `C:\RO-Lab\RO\RO\ro-server\docs\DESIGN.md` | 設計。§10 がクライアント関連 | 過去の OSS 調査あり |
| `C:\RO-Lab\notes\CLIENT_STRATEGY.md` | 方式比較と採用判断 | E2E 表は初期時点のまま残っている箇所あり。最新の試験結果は本ファイル §11 |
| `C:\RO-Lab\notes\CLIENT_BUILD_NOTES.md` | 初回棚卸し〜作業履歴 | 初期は「exe 不在で BLOCKED」。後で方針転換 |
| `C:\RO-Lab\notes\JAPANESE_CLIENT_TODO.md` | 初期の日本語化 TODO | **古い**。当時は jRO GRF 流用禁止と書いてあるが、後続指示で「手元の正規 jRO data.grf を読み取り専用で再利用」に方針変更済み |

---

## 1. いま何が動いているか（1枚絵）

現行クライアントは **ネイティブ kRO/jRO exe ではない**。

```
[Chrome]
  roBrowserLegacy (WebGL, GPL-3.0)
    Config.local.js
      packetver=20211103
      renewal=false
      langtype=2
      remoteClient = http://127.0.0.1:8000/client/
      socketProxy  = ws://127.0.0.1:8000/
        |
        | HTTP 資産 / WebSocket 中継
        v
[127.0.0.1:8000  ro-glue (自作 Node, 1プロセス)]
  1. 静的配信   C:\RO-Lab\client\robrowser\
  2. GRF配信    C:\Gravity\Ragnarok\data.grf （読み取り専用）
                + loose 上書き C:\RO-Lab\client\clientdata
                + loose 参照   C:\Gravity\Ragnarok （System/, BGM/ 等）
  3. WS→TCP    許可先のみ: 54.65.172.5:6900 / 6121 / 5121
        |
        | raw TCP（文字コード変換なし）
        v
[AWS rAthena Pre-Renewal]  ※サーバ側は FREEZE。変更しない
  login 6900 / char 6121 / map 5121
  PACKETVER 20211103
  文字列は CP932 運用
```

到達済み:

- 起動 → サーバ選択 `RO PreRE` → ログイン → char-server `rAthena-PreRE` → キャラ選択/作成 → map → ゲーム画面
- MOTD 日本語、新規日本語キャラ名、日本語チャット送受信は文字コード修正後に PASS
- サーバ変更: **NONE**

未実施 / 未完了:

- 英語 UI ラベル（Status / Inventory / Novice 等）の日本語化（`loadLua:true` 等は指示により未実施）
- 初心者修練場 NPC（Shion 等）の英語台詞（サーバスクリプト。クライアントでは直せない）
- 既存キャラ「シアレス」は修正前に UTF-8 で作られたため検証対象外

---

## 2. 制約・方針（守ること）

### 2.1 サーバ FREEZE

以下はクライアント側から変更しない。変更が不可避に見えても **Server-side Request として報告するだけ**。

- Terraform / AWS
- rAthena 設定 / PACKETVER / サーバコード
- 他エミュレータ（Auriga 等）への移行

優先順位: **現行 rAthena を維持 > 手元 jRO 公式データを使う > OSS クライアント > 他サーバ実装（最終手段・調査のみ）**

「jRO exe が使えない → rAthena を捨てる」には飛ばない。

### 2.2 資産・保護

禁止:

- 非公式ミラーから公式 RO クライアントを取得
- 非公式配布の data.grf / rdata.grf を取得
- crack / unpack 済み exe を取得
- GameGuard / Themida / WinLicense / anti-cheat 回避
- jRO 公式 exe の保護解除
- 第三者 RO サーバへの接続
- proprietary asset の再配布

許可して実施したこと:

- 手元の正規 jRO インストール `C:\Gravity\Ragnarok` を **読み取り専用**で参照
- jRO `Ragexe.exe` は **使わない**（別プロトコル、Themida + GameGuard）
- jRO `data.grf` はローカル配信のみ。127.0.0.1 以外に出さない
- GRF エントリの標準 DES フラグ復号は、exe 保護解除ではなく **GRF ファイル形式の互換実装**と判断して実施（roBrowser 同梱 `GameFileDecrypt.js` を import）

### 2.3 認証情報

アカウントは `player01` / `admin01` がサーバ側に存在する。パスワードはドキュメント・ログ・コードから探さない。ユーザーが設定して伝える。

本まとめにはパスワードを書かない。

---

## 3. サーバ側の事実（クライアントが合わせる値）

出典: `CLIENT_HANDOFF.md` / `README.md` / `docs/DESIGN.md` / `app/config.env`

| 項目 | 値 |
|---|---|
| Public IP | `54.65.172.5` |
| Login | `54.65.172.5:6900`（clientinfo / Config に書く唯一の接続先） |
| Char | `54.65.172.5:6121`（ログイン後にサーバが通知） |
| Map | `54.65.172.5:5121`（キャラ選択後にサーバが通知） |
| PACKETVER | `20211103`（`PACKETVER_RE` 範囲 20200902–20211118） |
| rAthena commit | `e985006171d2eb320ee512a653f4c83aea3d81b6` |
| モード | Pre-Renewal。3 次職なし |
| SERVER_NAME | `rAthena-PreRE` |
| `new_account` | no（`_M/_F` 自動登録なし） |
| `pincode_enabled` | no |
| `check_client_version` | 無効。`<version>55` は慣例値で接続可否に影響しない |
| `char_name_option` | 2（日本語名可、23 バイト） |
| パケット難読化 | PACKETVER > 20180307 は鍵 `(0,0,0)`。実質無効。クライアントは `packetKeys: false` |
| web-server 8888 | 未稼働 |
| 文字列運用 | **CP932** |
| アカウント | `admin01` (AID 2000000, group 99)、`player01` (AID 2000001) |

サーバ側で既に日本語化済み（HANDOFF）:

- カプラ、プロンテラ案内、一次職転職 NPC 6 種
- サポート職員 NPC（prontera 160,180）
- モンスター名 約 215、メッセージ 214、MOTD

サーバ側で英語のまま（クライアントでは直せない）:

- 初心者修練場の Shion など、上記以外の NPC スクリプト

クライアントが login に書くのは IP:6900 だけ。char/map はサーバ通知。glue の allow-list に 3 ポート全部入れているのは、通知された先へ WS 中継するため。

---

## 4. 方式比較と採用理由

3 案を比較し、**B + C** を採用。

| 観点 | A. Native 2021-11-03 RagexeRE | B. roBrowserLegacy | C. jRO data.grf 再利用 |
|---|---|---|---|
| PACKETVER 20211103 | ○ | ○ | ― |
| rAthena / Pre-RE | ○ / ○ | ○ / ○ | ― / ○ |
| Windows | ○ | ○ Chrome | ○ |
| 日本語表示 / IME | ○ / ○ | GRF テーブルは ○、内蔵 UI は英語残り / ○ HTML input | ○ |
| 公式・OSS のみ | **×** 公式配布終了 | ○ | ○ 手元正規品 |
| 保護回避不要 | ○ | ○ | ○ |
| 判定 | **不採用** | **採用** | **採用** |

A 不採用の理由:

- kRO 公式が配っているのは現行（2026）フルクライアントのみ
- 現行 kRO exe は PACKETVER が新しく、FREEZE サーバと不一致
- 2021-11-03 exe の入手経路は非公式ミラーのみ → 禁止事項に抵触
- 手元の jRO `Ragexe.exe`（2025-03-25）は系列違い + Themida/GameGuard

他 OSS を README/ソースで見て不採用にした例:

| 候補 | 理由 |
|---|---|
| Korangar | Rust nightly + Vulkan SDK。停止条件「大量 SDK」 |
| OpenMidgard | 2008 プロトコル |
| Lifthrasir | Aesir ローダのみ |
| lenaxia/rathena-client | プロトコルライブラリ。UI なし |
| roBrowserLegacy-RemoteClient-JS | ライセンス表記なし、DES 非対応 |

---

## 5. ディレクトリ構成

```
C:\RO-Lab\
  RO\RO\ro-server\          サーバ資料。クライアント作業では読むだけ。触らない
  tools\
    node\                   Node.js v22.23.2 portable（管理者権限不要、PATH 未変更）
    downloads\              取得 zip（SHA256 検証済み）
    roBrowserLegacy-dist\   公式 nightly 展開。未改変の原本
    roBrowserLegacy-src\    ソース commit e43b9b2。charset 修正の SoT。ここで build
    ro-glue\                自作 glue（server.mjs + ws）
    scripts\
      grf-inspect.ps1       GRF 0x200/0x300 読み取り専用調査
      make-login-overlay.ps1  欠ける kRO ログイン UI 19 ファイルを自作
  client\
    robrowser\              実行中の作業コピー（build 成果物 + Config.local.js）
    clientdata\             glue が GRF より優先する loose 上書き
      data\clientinfo.xml
      data\texture\유저인터페이스\   自作ログイン UI 19 ファイル
    data\                   ネイティブ exe 用に作った段階1 clientinfo（参考保管）
  backup\
    robrowser-dist-nightly-20260923\  charset 修正前の nightly Online.js 退避
  original\                 空。jRO は C:\Gravity を直接参照しコピーしない
  notes\                    本ファイルほか

C:\Gravity\Ragnarok\        jRO 公式インストール。読み取り専用。変更禁止
  Ragexe.exe                使わない
  data.grf                  使う（読み取りのみ）
  event.grf                 未使用（GRF 0x103）
  System\iteminfo.lub       ルーズ。いまは loadLua:false のため未使用
```

起動 URL: `http://127.0.0.1:8000/api.html?app=ONLINE`  
（`index.html` はビューア選択ランチャー。ゲーム本体は `api.html?app=ONLINE`）

---

## 6. コンポーネント仕様

### 6.1 roBrowserLegacy（ゲームクライアント）

| 項目 | 値 |
|---|---|
| リポジトリ | https://github.com/MrAntares/roBrowserLegacy |
| ライセンス | GPL-3.0 |
| 取得 | nightly `release-dist-web.zip`（build 2026-09-23 07:19:44）とソース zip |
| ソース commit | `e43b9b2bded117b945ebfd3d7604042546ca5354` |
| 実行形態 | Chrome 上の WebGL。Electron は使っていない |
| PACKETVER | `PacketVersions.js` に 20211103 あり。CHARACTER_INFO は RE 20211103 で int64 HP/SP |
| UI 世代 | packetver から自動選択。ログインは WinLoginV2（20181114〜）、インベントリは InventoryV3、BasicInfo は V4 |

設定の読み方:

1. `Config.js` → `window.ROConfigBase`（既定。`remoteClient` が `https://grf.robrowser.com/`）
2. `Config.local.js` → `window.ROConfigLocal`（上書き）
3. `api.html` が deepMerge して `window.ROConfig`

**絶対条件**: `remoteClient` をローカル glue に固定すること。既定の grf.robrowser.com には資産を取りに行かない。

現行 `C:\RO-Lab\client\robrowser\Config.local.js`:

- `address 54.65.172.5` / `port 6900` / `version 55` / `langtype 2`
- `packetver 20211103` / `renewal false` / `packetKeys false`
- `socketProxy ws://127.0.0.1:8000/`
- `remoteClient http://127.0.0.1:8000/client/`
- `adminList [2000000]`
- `skipIntro true`（ローカル GRF ドラッグ不要）
- `skipServerList false`（サーバ一覧を見せる）
- `loadLua false`（英語 UI 対応は未着手）
- CashShop / Bank / Attendance / Roulette / Achievements は off

### 6.2 ro-glue（静的 + GRF + WS 中継）

場所: `C:\RO-Lab\tools\ro-glue\server.mjs`  
ライセンス: GPL-3.0-or-later（DES 復号に GPL モジュールを使うため）  
依存: `ws` ^8（MIT）のみ

起動例:

```powershell
cd C:\RO-Lab\tools\ro-glue
C:\RO-Lab\tools\node\node.exe server.mjs --port 8000 `
  --static "C:\RO-Lab\client\robrowser" `
  --grf "C:\Gravity\Ragnarok\data.grf" `
  --loose "C:\RO-Lab\client\clientdata" --loose "C:\Gravity\Ragnarok" `
  --allow "54.65.172.5:6900,54.65.172.5:6121,54.65.172.5:5121" `
  --decrypt "C:\RO-Lab\tools\roBrowserLegacy-src\src\Loaders\GameFileDecrypt.js"
```

任意: `--dump-rx C:\RO-Lab\notes\rx-dump.txt`  
サーバ→クライアント方向の hex のみ。クライアント→サーバは書かない（パスワードを残さない）。

エンドポイント:

| 経路 | 役割 |
|---|---|
| `GET /` および静的ファイル | dist 配信。`/` は `api.html` |
| `GET /client/<path>` | 資産。loose 優先、なければ GRF |
| `POST /client/` body `filter=<regex>` | GRF ファイル名検索 |
| `POST /client/batch` JSON `{files:[...]}` | 一括取得（base64） |
| `GET /__status` | hits/misses/GRF 情報 |
| `WS /<ip>:<port>` | TCP 中継。allow-list 外は 403 |

GRF 実装要点:

- 0x200 と 0x300（Event Horizon、64bit offset）を読む
- テーブルは zlib。エントリ type 0x02/0x04 は標準 Gravity DES
- ファイル名は EUC-KR バイト。ブラウザは windows-1252 として送ることがあるので、latin1 生バイトキーと EUC-KR 復号キーの両方で照合
- UTF-8 パーセントエンコード（`유저인터페이스`）も受け付ける
- 不正な UTF-8 パーセント列は latin1 として解釈（EUC-KR 生パス対策）
- 127.0.0.1 のみ listen。payload は **raw bytes 透過**。文字コード変換しない

### 6.3 ログイン UI オーバーレイ

jRO data.grf には旧 `win_login.bmp` 系しかない。roBrowser は packetver ≥ 20181114 で kRO 新ログイン UI を要求する。欠ける 19 ファイルを自作して loose 配置した。

生成スクリプト: `C:\RO-Lab\tools\scripts\make-login-overlay.ps1`  
出力先: `C:\RO-Lab\client\clientdata\data\texture\유저인터페이스\`

| ファイル | 内容 |
|---|---|
| `login_interface/bg_login.tga` | 301×132 自作パネル |
| `login_interface/bt_start_{normal,over,press}.bmp` | 84×84 Login ボタン |
| `login_interface/bt_join_{normal,over,press}.bmp` | 84×21 小ボタン |
| `t_배경1-1.bmp` … `t_배경3-4.bmp` | 手元 `bgi_temp.bmp`（1280×720）を 4×3 分割 |

`C:\Gravity` には書いていない。再配布しない。

---

## 7. 文字コード設計（重要）

### 7.1 問題

初回接続時:

- MOTD が `ƒo�[ƒWƒ‡ƒ“…` に化けた
- サーバ送信 raw は CP932 で正しい（例: `83 6F 81 5B` = 「バー」）
- glue は変換していない
- 壊れ箇所はブラウザ内デコード

原因:

- `BinaryReader.getString()` が `decode(..., 'utf-8')` → `smartDecode`（UTF-8 成功なら UTF-8、失敗なら `userCharset`）
- `userCharset` は GRF 用に `windows-1252` 固定
- `LoginEngine` は langtype=2 → `shift-jis` を **ログに出すだけ** で `setCharset` していなかった
- 送信 `BinaryWriter` は **UTF-8 固定**。そのため修正前に作ったキャラ「シアレス」は UTF-8 で DB に入った

GRF 由来（msgstringtable / mapnametable / 所持アイテムタイトル等）は最初から日本語で出ていた。壊していたのは **ネットワーク文字列だけ**。

### 7.2 方針

**GRF/DB charset と network charset を分離する。**  
既に読めていた jRO テーブルを壊さないことを優先。

| 経路 | charset | 設定箇所 |
|---|---|---|
| GRF / txt テーブル | `userCharset` = `windows-1252`（ファイル名バイト用）+ `userCharpage` = langtype 由来 `shift-jis`（テキスト中身） | `DBManager.js`。**変更していない** |
| ネットワーク送受信 | `networkCharset`。langtype=2 → `shift-jis`。`server.networkCharset` で上書き可 | `LoginEngine` が `setNetworkCharset` |

iconv-lite（roBrowser バンドル）では `shift-jis` / `windows-932` / `cp932` は **同一テーブル**。実測で差なし。名前は langtype 検出どおり `shift-jis` を使う。中身は CP932 互換。

encode 時、IME が出しやすい JIS 系 Unicode を CP932 側へ正規化:

- U+301C WAVE DASH → U+FF5E
- U+2016 → U+2225
- U+2212 → U+FF0D
- U+00A2/A3/AC → 全角記号

固定長フィールドは文字境界で切り詰め（リードバイトだけ送らない）。

`readBinaryString()`（マップ名 `.gat`、スキル内部名などバイト列）は charset 変換しない。ローダ類はこちらを使うので GRF マップ読みに影響しない。

### 7.3 修正したソース（SoT）

恒久対応は **src を直して build**。Online.js 直接編集はしない。

| ファイル | 変更 |
|---|---|
| `src/Utils/CodepageManager.js` | `networkCharset` / `setNetworkCharset` / `decodeNetwork` / `encodeNetwork` 追加 |
| `src/Utils/BinaryReader.js` | `getString` → `decodeNetwork` |
| `src/Utils/BinaryWriter.js` | `setString` / `writeString` の UTF-8 固定を `encodeNetwork` に |
| `src/Engine/LoginEngine.js` | langtype から `setNetworkCharset`。GRF の `setCharset` は呼ばない |

`decodeNetwork` は従来どおり UTF-8 を先に試し、不正なら networkCharset。ASCII のみのサーバ名などは UTF-8 でも同じ。

### 7.4 再ビルド手順

ソースツリーに lock が無く、`npm install` は peer 解決で落ちることがある。実作業では:

```powershell
cd C:\RO-Lab\tools\roBrowserLegacy-src
$env:PATH = "C:\RO-Lab\tools\node;$env:PATH"
# electron 等は不要。ignore-scripts + legacy-peer-deps
npm install --no-save --legacy-peer-deps --ignore-scripts --omit=optional --no-audit --no-fund `
  vite@^8.0.1 @rollup/plugin-alias@^6.0.0 terser@^5.19.4 bson@^7.2.0 `
  granny-ro-js@~1.5.0 lodash-es@^4.18.1 rijndael-js@^2.0.0 ws@^8.18.0
npm install --no-save --legacy-peer-deps --ignore-scripts --no-audit --no-fund `
  @rolldown/binding-win32-x64-msvc@1.2.9 lightningcss-win32-x64-msvc@1.33.0
node ./applications/tools/builder-web.mjs -O
# 出力: dist\Web\Online.js / ThreadEventHandler.js / PathFindingWorker.js
# 作業コピーへコピーする前に nightly 原本を backup へ退避すること
```

修正後 build の Online.js には `[LOGIN] Network Encoding` / `[LOGIN] GRF Encoding` のログが出る。コンソールで `shift-jis` と `windows-1252` が分かれていれば分離成功。

---

## 8. jRO data.grf の事実

パス: `C:\Gravity\Ragnarok\data.grf`（約 4.57 GB、2025-04-27）

| 項目 | 値 |
|---|---|
| 署名 | `Event Horizon` |
| version | 0x300 |
| ファイル数 | 252,721 |
| テーブル | zlib |
| DES フラグ | 43,604 エントリ（0x02/0x04） |
| ファイル名 | EUC-KR（`유저인터페이스`, `몬스터` 等。kRO 形式パス） |

読めたもの:

- マップ `prontera.gat/gnd/rsw`
- `msgstringtable.txt`, `idnum2itemdisplaynametable.txt`, `mapnametable.txt`
- スプライト `poring.spr/act`（DES 付き）
- UI `win_login.bmp` 等
- loose `System\iteminfo.lub`

足りないもの（kRO 新 UI / 一部 2018 以降ファイル）:

- ログイン新 UI 19 ファイル → 自作で補完済み
- `skilldesctable.txt`（404。スキル説明は内蔵英語のまま）
- `SystemEN/Towninfo.lub`（公式翻訳ファイル。無くても致命傷ではない）
- 一部 kRO 専用ボタン（roulette, adventurer agency 等）。該当 UI は Config で off

`loadLua: false` のため、いま参照している日本語テーブルは主に txt（msgstringtable / mapnametable / idnum2item*）。`iteminfo.lub` と skillinfoz lub は未ロード。

---

## 9. 英語表示の原因（未修正。仕様として残している）

文字化けとは別問題。英語が出る場所は **roBrowser 内蔵 JS/HTML** を見ている。

| 画面の英語 | 参照元 |
|---|---|
| `Novice` | `DB/Monsters/MonsterTable.js`（スプライト名兼用の英語テーブル）。`BasicInfo` がこれを job 名として表示 |
| スキル名 | `DB/Skills/SkillInfo.js` 内蔵英語 |
| `Status (Alt + A)` 等メニュー | 内蔵 HTML |
| `Disconnected from Server` | 内蔵 UI 文字列 |
| WorldMap の `Midgard` / `Hugel Field` | `DB/Map/WorldMap.js` 内蔵英語。個別マップ名ラベルは mapnametable 由来で日本語が出る |
| 修練場 NPC（Shion） | **サーバスクリプトが英語**。クライアント非対象 |

日本語で出ているもの（jRO GRF / msgstringtable）:

- MOTD、チャット設定文、マップ表示名「初心者修練場 5-1」
- 所持アイテムウィンドウタイトル、削除予約、ゲーム開始
- アイテム表示名テーブル（txt）。ただし空インベントリでは見えない

次にやるなら（未実施）:

1. `loadLua: true` + jRO `System/iteminfo.lub` / skillinfoz
2. 職業名を内蔵 `MonsterTable` ではなく日本語テーブルへ差し替え
3. メニュー HTML の `data-text`（msgstringtable ID）が実際に解決されているか確認

---

## 10. 「バグに見えるが仕様」だったもの

### 所持アイテム

空インベントリ（0/100）で水色の楕円が並ぶのは、jRO の `basic_interface/itemwin_mid.bmp`（32×32 スロット画像）をタイルしているため。資産 404 ではない。左の縦タブは InventoryV3（kRO 2018 以降風）のデザイン。

旧型インベントリに戻す改造は可能だが未実施。

### ワールドマップ

roBrowser 独自 WorldMap。赤枠はダンジョン、ラベルは mapnametable の日本語。下半分が黒いのはブラウザ枠の高さ不足で窓が切れているだけ。セレクトの `Midgard` は内蔵英語テーブル。

### NPC 英語

サーバ側スクリプト。HANDOFF 記載の日本語化範囲外。直すなら Server-side Request。

---

## 11. 試験結果（2026-09-23 時点）

| 項目 | 結果 | 備考 |
|---|---|---|
| 起動 | PASS | jRO 背景表示 |
| サーバ選択 RO PreRE | PASS | |
| ログイン画面 | PASS | 自作オーバーレイ |
| ログイン認証 player01 | PASS | |
| char-server 一覧 | PASS | `rAthena-PreRE` |
| キャラ選択 | PASS | |
| 新規日本語キャラ作成 | PASS | 「ユンヌ」。サーバ往復が CP932 バイト |
| map 着地 | PASS | 初心者修練場 5-1 |
| MOTD 日本語 | PASS | 修正後。修正前は 1252 化け |
| 日本語チャット送信 | PASS | 「あああ」「うんこ」が CP932 で往復 |
| 既存キャラ「シアレス」 | 対象外 | 修正前 UTF-8 保存 |
| カプラ/サポート職員の日本語 | 未確認 | プロンテラ到着後に確認する |
| 職業名 Novice 等 | 英語のまま | 内蔵テーブル。未対応 |
| 修練場 NPC | 英語 | サーバ仕様 |

3 ポート TCP 到達はクライアント PC から OK。

---

## 12. 手元資産の棚卸し（参考）

`C:\Gravity\Ragnarok` が唯一の公式クライアント。

| ファイル | 備考 |
|---|---|
| Ragexe.exe | 2025-03-25、Themida（`.winlice` `.boot` `.vm_sec`）、GameGuard 同梱。**不使用** |
| Ragnarok.exe | パッチャー |
| data.grf | 使用（読み取り） |
| event.grf | 未使用 |
| data/ | 空 |
| DATA.INI / clientinfo.xml | ルーズには無い（jRO 形式） |

kRO 2021-11-03 RagexeRE は手元に無い。探して非公式取得はしない。

段階1 `clientinfo.xml`（ネイティブ exe 用、参考）は `C:\RO-Lab\client\data\` に BOM なし ASCII。roBrowser はこれを必須とせず、`Config.local.js` の `servers[]` を使う。glue の loose にも同内容を置いてある。

---

## 13. 判断ログ（後から覆すとき用）

1. GRF DES 復号はファイル形式互換であり、exe 保護解除ではない。不許可なら DES 付き 4 万エントリ（UI・スプライト・多数マップ）が読めなくなる。
2. Node portable zip は「大量 SDK」に当たらない。管理者権限不要。
3. charset 修正は src → build。Online.js 直接編集は PoC 限定で、今回の恒久対応には使っていない。
4. 英語 UI 対応（loadLua 等）は文字コード修正の後、指示待ち。先に混ぜない。
5. サーバ文字列は CP932 のまま。クライアントだけ合わせる。

---

## 14. よくある次の作業

文字コードは一段落している。残作業の優先候補:

1. プロンテラでカプラ / サポート職員（160,180）の日本語台詞確認（テスト 5 の残り）
2. 英語 UI（職業名、スキル名、メニュー）— `loadLua` と内蔵テーブル差し替え。サーバ変更不要
3. 空インベントリ見た目 / WorldMap の見やすさ — UI 世代または CSS。必須ではない
4. 修練場 NPC 日本語化 — **サーバ側**。依頼するなら Server-side Request
5. 既存 UTF-8 キャラ「シアレス」— サーバ DB を触らず捨てて、新キャラを使う

起動し直すとき:

1. glue が `127.0.0.1:8000` で生きているか確認
2. Chrome または Cursor ブラウザで `http://127.0.0.1:8000/api.html?app=ONLINE`
3. キャッシュ疑いなら URL に `?v=` を付ける（Online.js は 12 MB）

glue 停止:

```powershell
Get-Process node | Where-Object { $_.Path -like 'C:\RO-Lab\tools\node\*' } | Stop-Process
```

---

## 15. 用語

| 語 | 意味 |
|---|---|
| PACKETVER | クライアント/サーバが合意するパケット日付。本環境は 20211103 |
| langtype 2 | japan。roBrowser では network charset 検出に使う |
| CP932 | Windows 日本語。Shift_JIS + NEC/IBM 拡張。サーバ運用 |
| GRF 0x300 | Event Horizon。64bit offset |
| loose | GRF より優先する生ファイル。`clientdata` と `C:\Gravity\Ragnarok` |
| glue | 自作 Node。静的 + GRF + WS→TCP |
| FREEZE | サーバ側を変えない合意 |
| WinLoginV2 / InventoryV3 | packetver 連動の roBrowser UI 世代 |

---

## 16. この文書を使うときの注意

- パスワード・アカウント秘密はここに無いし、ログから探さない
- `JAPANESE_CLIENT_TODO.md` の「jRO GRF 禁止」は旧方針。現行は手元正規 data.grf の読み取り再利用
- `CLIENT_STRATEGY.md` §6 の E2E 表は初期値のまま残っている。試験の最新は本ファイル §11
- サーバ資料の clientinfo / WARP 手順はネイティブ exe 用。現行実行系は Config.local.js + glue
- ソースの正は `C:\RO-Lab\tools\roBrowserLegacy-src\src\`。実行ファイルは `C:\RO-Lab\client\robrowser\Online.js`（build 成果物）
