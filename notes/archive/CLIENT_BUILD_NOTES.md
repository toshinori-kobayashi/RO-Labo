> **ARCHIVED / HISTORICAL（2026-09-24）** — この文書は現在の仕様ではありません。作成時点（2026-09-23）の調査・作業記録として残しています。
> 現行仕様: クライアントは [client/README.md](../../client/README.md)、全体構成は [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)、現在地は [docs/CURRENT_STATUS.md](../../docs/CURRENT_STATUS.md)。2026-09-24 に `notes/archive/` へ移動済み。

# CLIENT_BUILD_NOTES

作成日: 2026-09-23
担当: Windows クライアント構築・接続検証
対象サーバ: rAthena Pre-Renewal / PACKETVER 20211103 / 54.65.172.5 (login 6900, char 6121, map 5121)

---

## 0. 結論サマリ（2026-09-23 更新）

**Client Result: PARTIAL PASS（起動 → サーバ選択 → ログイン画面まで PASS。認証は `player01` パスワード待ち）**

> 2026-09-23 追記: 方針を「ネイティブ kRO exe」から「OSS クライアント roBrowserLegacy + 手元 jRO data.grf（読み取り専用）」に変更。
> 詳細・比較・根拠は `CLIENT_STRATEGY.md` を正とする。以下 §1〜§8 の初回記述は履歴として残し、変わった点を各節に追記。

- 手元にある唯一の RO クライアントは `C:\Gravity\Ragnarok`（jRO 公式クライアント）。exe は使わない（保護付き・別系列）。
- kRO 2021-11-03 RagexeRE は公式配布終了。非公式ミラーからの取得は禁止 → ネイティブ exe 方式は不採用。
- 代替: roBrowserLegacy（GPL-3.0, commit e43b9b2）Web ビルド + 自作 glue（GRF 配信 + WS→TCP 中継）。
- jRO `data.grf`（GRF 0x300）は標準形式で読める。kRO 依存の UI 画像 19 点だけ自作で補完。
- サーバ変更: **NONE**。
- ネットワークは 3 ポートとも到達 OK。

---

## 1. 参照ドキュメントの確認結果

| ファイル | 結果 |
|---|---|
| CLIENT_HANDOFF.md | 初回探索では見つからず → **2026-09-23 に `C:\RO-Lab\RO\RO\ro-server\CLIENT_HANDOFF.md` で確認・全文読了**（SoT） |
| README.md | 同上 → `C:\RO-Lab\RO\RO\ro-server\README.md` 読了（PACKETVER 20211103、`player01`/`admin01` は存在・パスワードは `scripts/set-password.sh` で設定） |
| docs/DESIGN.md | 同上 → `C:\RO-Lab\RO\RO\ro-server\docs\DESIGN.md` §2/§10 読了（§10.5 過去の OSS 調査、§10.6 クライアント要件） |

SoT から取り込んだ事実: `new_account: no`、`pincode_enabled: no`、`char_name_option: 2`（日本語名可）、`check_client_version` 無効、
web-server 8888 未稼働、`SERVER_NAME=rAthena-PreRE`、サーバ側日本語化は済（Kafra/案内/転職 NPC/サポート職員 NPC/モンスター名/メッセージ）。
`C:\RO-Lab\RO` 配下のサーバ資産は別担当のため触っていない。

---

## 2. クライアント資産の棚卸し

### 2.1 探索範囲

- `C:\Users\admin\Desktop`（ワークスペース）: RO 関連ファイル無し
- `C:\Users\admin\Downloads`: RO 関連ファイル無し
- `C:\Users\admin\Documents`: RO 関連ファイル無し
- `C:\Program Files`, `C:\Program Files (x86)`: WARP / NEMO / Gravity / GungHo 関連ディレクトリ無し
- `F:\efc`（Cursor の別プロジェクト）: depth 2 で RO 関連ファイル無し
- `C:\Gravity\Ragnarok`: **jRO 公式クライアント発見**（唯一の候補）
- `C:\RO-Lab`: 存在しなかったため新規作成

※ 全ドライブ再帰検索は範囲が広すぎるため未実施。上記以外の場所に kRO クライアントがある場合は場所の指示が必要。

### 2.2 `C:\Gravity\Ragnarok` の exe 一覧

| ファイル | サイズ | PE タイムスタンプ (UTC) | SHA256 | 備考 |
|---|---|---|---|---|
| Ragexe.exe | 5,580,216 | 2025-03-25 03:12:29 | `306992D546F93D44509C254A0FFBB8BC8A715504495EAF5448691573DB1A45EA` | ゲーム本体。VersionInfo 無し。パック済み |
| Ragnarok.exe | 3,579,328 | 2024-09-06 05:16:09 | `0C05E62248076627EE217F700F78B8BE702E497AF427677BF15CABF206D086B9` | パッチャー/ランチャー (v2.0.0.1) |
| Setup.exe | 1,711,088 | 2023-12-05 07:30:48 | `9F31C70E48A6BBB9C301DB1AC4D4DF13B5F67521B4CE62CF94DCB8E06ABEE8C1` | 設定ツール |
| ROEXEURI.exe | 30,312 | 2022-06-10 03:22:41 | `994479E92014570C497237A3AAE0FC31CD06E603BC29A81D2AE4174AA0B65FF0` | URI ハンドラ |

**RagexeRE 系 exe: 無し。** `Ragexe*.exe` は上記 1 本のみ。

### 2.3 Ragexe.exe が jRO 公式・保護付きであると判断した根拠

- 同ディレクトリに `RagnarokJP.ini`（内容は暗号化済みバイナリ）、`GameGuard/`（npgg 系 .erl 34 ファイル）、`GameGuard.des`
- `patch2.txt` は jRO パッチ履歴（`2009-05-21sro_13-1bgm_jp.rgz` 〜 `2025-04-24main05.gpf`、最終番号 5850）
- `_tmpEmblem/` に jRO ワールド名 `Breidablik_*.ebm`
- PE セクション: 名前無しセクション ×5（VSize ≫ RawSize）、`.vm_sec`、`.winlice`（RawSize 0 / VSize 0x44C000）、`.boot`
  → Themida / WinLicense 系パッカーの典型的な構成
- ASCII 文字列スキャン: `clientinfo.xml` / `sclientinfo.xml` / `data.grf` / `DATA.INI` / `ExternalSettings` / `SelectKoreaClientInfo` / `1rag1` 等が **0 件**
  → 通常の kRO exe なら平文で存在する文字列が見えない = コードが暗号化されている

### 2.4 PACKETVER 20211103 との整合性

| 観点 | 判定 |
|---|---|
| exe 世代 | 2025-03-25 ≠ 2021-11-03。**不一致** |
| exe 系列 | jRO Ragexe ≠ kRO RagexeRE。jRO は独自パケット/独自暗号化のため、日付以前に **系列自体が非互換** |
| WARP 適用可否 | Themida/WinLicense 保護のためそのままでは **不可**。アンパックは protection 回避に該当し **禁止** |
| GameGuard | 自前サーバへ接続するには GameGuard を無効化する必要があり、anti-cheat 回避に該当し **禁止** |
| データ | `data.grf`(4.5GB)/`event.grf` は jRO 公式データ。無断流用禁止のため **不使用** |

→ 「おそらく互換」で進める余地は無く、**不足資産**として報告。

### 2.5 data / GRF / テーブル類

| 項目 | 観測結果 |
|---|---|
| `data/` フォルダ | 存在するが **空**（0 ファイル） |
| GRF | `data.grf` (4,569,872,560 B, 2025-04-27), `event.grf` (3,565,831 B, 2022-11-30) — いずれも jRO 公式 |
| DATA.INI | **無し**（jRO は exe 内部で GRF 名を持つ形式） |
| clientinfo.xml / sclientinfo.xml | ルーズファイルとしては **無し**（jRO は GRF 内 or 暗号化 ini 経由と推定。未検証） |
| msgstringtable.txt / mapnametable.txt / questid2display.txt / cardprefixnametable.txt | ルーズファイルとしては **無し**（GRF 内にあるかは未検証。jRO データは不使用のため確認不要） |
| luafiles514/ | `System\LuaFiles514\`（MsgString.lub, OptionInfo.lub の 2 ファイルのみ） |
| itemInfo | `System\iteminfo.lub` (890,661 B) — jRO 版 |
| skillinfoz | ルーズファイル無し |
| UI/ | ルーズファイル無し。`skin\default\` に 432 ファイル |
| Font | `System\font\SCDream4.otf`, `SCDream6.otf` |
| WARP/NEMO patch 済みか | 保護付き公式 exe のため **未パッチ**（公式そのまま） |

### 2.6 「何を使って接続しようとしているのか」の確定

**現状、接続に使える正規のクライアント exe は手元に無い。**
使用予定（入手後）: kRO 2021-11-03 RagexeRE + kRO data.grf/rdata.grf（正規入手品）+ WARP。

---

## 3. 作業ディレクトリ

```
C:\RO-Lab\
  original\           元資産（変更禁止）。現在は README.txt のみ。jRO 資産は意図的に置かない
  client\
    data\
      clientinfo.xml  段階1 最小構成（ASCII のみ、BOM 無し、CRLF、442 B）
      sclientinfo.xml 同内容（RagexeRE がどちらを読むか実機未確認のため両方配置）
  backup\             空（まだ変更対象ファイル無し）
  notes\
    CLIENT_BUILD_NOTES.md   本ファイル
    JAPANESE_CLIENT_TODO.md 日本語化 TODO
```

### 3.1 clientinfo.xml（使用内容）

```xml
<?xml version="1.0" encoding="euc-kr" ?>
<clientinfo>
    <servicetype>japan</servicetype>
    <servertype>sakray</servertype>
    <connection>
        <display>RO PreRE</display>
        <desc>Pre-Renewal Test Server</desc>
        <balloon>EXP x10 / Drop x5</balloon>
        <address>54.65.172.5</address>
        <port>6900</port>
        <version>55</version>
        <langtype>2</langtype>
    </connection>
</clientinfo>
```

検証済み: 先頭バイト `3C 3F 78 6D 6C`（BOM 無し）、非 ASCII バイト 0、servicetype/servertype は clientinfo 直下。

### 3.2 clientinfo 読み込み経路（未確定）

- 一般に kRO Ragexe は `data\clientinfo.xml`、RagexeRE は `data\sclientinfo.xml` を読むとされるが、
  **2021-11-03 RagexeRE の実機挙動は未確認**。
- 読み込み元（ルーズ data/ か GRF 内か）は WARP の `Read Data Folder First` / `Enable Multiple GRFs` (DATA.INI) の適用状況で変わる。
- 判定基準: サーバ一覧に `RO PreRE` が表示されたら読み込み成功。
- exe 入手後、まず両ファイルを置いた状態で起動し、どちらを消しても表示が残るかで読み込み先を特定する。

---

## 4. ネットワーク確認（手順7）

実行日時: 2026-09-23 16:2x JST、送信元 192.168.11.5

| 宛先 | 結果 |
|---|---|
| 54.65.172.5:6900 (login) | `TcpTestSucceeded : True` |
| 54.65.172.5:6121 (char) | `TcpTestSucceeded : True` |
| 54.65.172.5:5121 (map) | `TcpTestSucceeded : True` |
| DNS `ec2-54-65-172-5.ap-northeast-1.compute.amazonaws.com` | A = 54.65.172.5 |

ICMP ping は False（AWS SG で ICMP 未許可と推定。TCP には影響無し）。

補足: プロトコルレベル確認（存在しないアカウント名で 0x0064 を 1 回送り 0x006A 応答を見る）は
本作業のクライアント優先フローから外れるため **未実施**。必要なら別途承認の上で実施可能。

---

## 5. WARP patch 計画（未適用）

exe が無いため 1 件も適用していない。入手後の適用計画のみ記載。

| Patch 名 | 必要理由 | 想定副作用 | 適用 |
|---|---|---|---|
| Disable 1rag1/1sak1 type parameters | ランチャー経由の起動引数チェックを外し、exe 直接起動を可能にする | 無し（公式ランチャー不使用のため） | 未 |
| Read Data Folder First | `data\clientinfo.xml` 等のルーズファイルを GRF より優先して読む | GRF 内と重複するファイルはルーズ側が勝つ | 未 |
| Enable Multiple GRFs (DATA.INI) | 上記の代替。複数 GRF の読込順を DATA.INI で制御 | DATA.INI 記述ミスで起動失敗 | 未（Read Data Folder First で足りれば不要） |
| Always load Korea ExternalSettings lua file | servicetype=japan でも kRO 用 `ExternalSettings_kr.lub` を読み、jRO 用ファイル不在による起動失敗を防ぐ | 無し | 未 |
| Always Call SelectKoreaClientInfo() | servicetype=japan でも kRO の clientinfo 読込経路を使う | clientinfo の読込ファイル名が変わる可能性（3.2 参照） | 未 |
| Customize Font name | 日本語フォント指定（段階2以降） | 段階1 では不要 | 未（後回し） |
| Disable filename check | exe 名を変更する場合のみ | 無し | 未（exe 名変更しない前提） |
| Disable Packet Encryption | サーバ側 PACKET_OBFUSCATION 無効なら必要な場合あり | rAthena 既定は obfuscation 有効のため通常 **不要** | 不要 |
| Use Ascii on All LangTypes | langtype=2 で文字化けする場合の緊急用 | 日本語表示が潰れる | 最初は使わない |

---

## 6. 試験結果（E2E）

### 6.1 ネイティブ exe 方式（初回）

| Phase | 内容 | 結果 |
|---|---|---|
| 1 | exe 起動 | **FAIL（未実施）** — 対応 exe 無し（方式自体を不採用に変更） |

### 6.2 roBrowserLegacy 方式（2026-09-23）

| Phase | 内容 | 結果 |
|---|---|---|
| 1 | クライアント起動（Chrome, http://127.0.0.1:8000/api.html?app=ONLINE） | **PASS** |
| 2 | server list に RO PreRE | **PASS** |
| 3 | ログイン画面表示 / 6900 login-server 接続 | 画面 **PASS** / TCP 到達 PASS（クライアント経由の接続は Phase 4 と同時） |
| 4 | ログイン認証 | **未実施** — `player01` パスワード設定待ち |
| 5 | char-server 遷移 | 未実施 |
| 6 | キャラ作成/選択 | 未実施 |
| 7 | map-server 遷移 | 未実施 |
| 8 | ゲーム画面 | 未実施 |

スクリーンショット: `%LOCALAPPDATA%\Temp\cursor\screenshots\ro-e2e-01-boot.png`, `ro-e2e-02-login.png`
glue ログ: `C:\RO-Lab\notes\glue-server.log`（資産 404 は自作オーバーレイ適用後 0 件）

---

## 7. 障害記録

### A-1. exe boot failure（実行前 blocker）

- 現象: 起動対象となる kRO 2021-11-03 RagexeRE が存在しない
- 再現方法: `Get-ChildItem C:\Gravity\Ragnarok -Filter Ragexe*.exe` → jRO Ragexe.exe (2025-03-25) のみ
- 直前の変更: 無し
- ログ: 本ノート 2.2 / 2.3
- 仮説: 過去に kRO クライアントを導入した履歴が無い（Cursor プロジェクト履歴・ダウンロードフォルダにも痕跡無し）
- 次の最小変更: ユーザーが正規入手した kRO 2021-11-03 RagexeRE と kRO GRF を `C:\RO-Lab\original\` に配置 → `client\` へコピー → Phase 1 再試験

---

## 8. 未確認事項

- [x] CLIENT_HANDOFF.md の所在 → `C:\RO-Lab\RO\RO\ro-server\`
- [ ] ~~2021-11-03 RagexeRE が clientinfo/sclientinfo のどちらを読むか~~（ネイティブ exe 方式は不採用のため対象外）
- [ ] ~~手元 WARP の版~~（同上。WARP は使用しない）
- [x] サーバ側 packet obfuscation → rAthena `clif_obfuscation.hpp`: PACKETVER > 20180307 は鍵 (0,0,0) = 実質無効。roBrowser 側 `packetKeys:false` で整合
- [x] サーバ側 `client_version` チェック → `check_client_version` 無効（README/HANDOFF）
- [x] テスト用アカウント → `new_account: no`。`player01`(2000001) が存在、パスワードは SRE が `set-password.sh` で設定する運用
- [ ] ~~kRO data.grf / rdata.grf の世代~~ → 手元 jRO data.grf で代替（kRO 依存 UI 19 点のみ自作補完）
- [ ] 日本語チャット表示 / IME 入力の実挙動（Phase 8 到達後に確認）
- [ ] `loading*.jpg` が jRO data.grf に無い場合のローディング画面（黒背景で進行するだけと想定）
