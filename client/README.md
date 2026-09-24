# RO-Labo クライアント

`client/` の SoT（Single Source of Truth）です。「いま動いているクライアントは何か」を、後続の作業者や引き継ぎ先の AI に渡すための現行仕様をまとめています。

過去の調査・作業記録は `notes/`（HISTORICAL。各ファイル先頭に注記があります）にあります。サーバ構築・Terraform・rAthena の運用手順はここには書きません（`server/docs/`、統合予定パス）。全体のアーキテクチャ図・責務境界は [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)、現在の完成状況は [`../docs/CURRENT_STATUS.md`](../docs/CURRENT_STATUS.md) を参照してください。

---

## これは何か

Windows 上の Chrome で動く、rAthena Pre-Renewal 向けブラウザクライアントです。公式の `Ragexe.exe` ではありません。起動 URL は `http://127.0.0.1:8000/api.html?app=ONLINE`（`index.html` はビューア用ランチャーで、ゲーム本体ではありません）。

別アカウントならブラウザを 2 窓開けます。窓ごとに WebSocket と TCP が 1 本ずつです。同じアカウントを 2 窓で使うと、後から入った方が先の接続を切ります。

## roBrowserLegacy

- 上流: `MrAntares/roBrowserLegacy`（GPL-3.0）。基準コミットは `../README.md`「外部依存」を参照。
- ソースの正本は `tools/roBrowserLegacy-src/src/`（Phase 2 で `client/roBrowserLegacy-src/` へ移動予定）。上流との差分は 8 ファイルだけで、目的・要点は [`docs/PATCHES.md`](docs/PATCHES.md) が正本です。
- 実行コピーは `client/robrowser/`。ゲーム起動に必要なのは `Online.js`、`ThreadEventHandler.js`、`PathFindingWorker.js`、`api.html`、`api.js`、`Config.js`、`Config.local.js` の 7 つです。同ディレクトリにある `EffectViewer.js` などのビューア 7 本（各 12MB）はゲーム起動に不要です（削除は Phase 2 以降）。
- 再ビルド手順は [`docs/BUILD.md`](docs/BUILD.md)。

## ro-glue

静的配信・GRF/loose 資産配信・WebSocket→TCP 中継を行う自作 Node です（`tools/ro-glue/server.mjs`、Phase 2 で `client/ro-glue/` へ移動予定）。**パケットの改変・文字コード変換は一切しません**（バイト列透過）。`remoteClient` はローカル glue に固定してあり、既定の `https://grf.robrowser.com/` へは行きません。CLI 全オプション、エンドポイント、GRF 実装要点、セキュリティ上の前提は [`docs/GLUE.md`](docs/GLUE.md) が正本です。起動コマンドの例は本書の「起動手順」にあります。

## jRO data.grf と使わないもの

- ユーザー所有の jRO 公式インストール `C:\Gravity\Ragnarok\data.grf`（読み取り専用）を資産元として使います。リポジトリには含めず、127.0.0.1 以外へは出しません。
- `Ragexe.exe` は使いません。Themida/WinLicense と GameGuard 付きで、プロトコル系列もこのサーバとは別です。
- `client/data/clientinfo.xml` と `sclientinfo.xml` はネイティブ exe 用に作った遺物です。roBrowser はこれらを読みません。

## clientdata（loose）

資産の解決順は `client/clientdata/` → `C:\Gravity\Ragnarok`（`System/` `BGM/` 等）→ GRF です。

`client/clientdata/data/texture/유저인터페이스/login_interface/` に、jRO の `data.grf` には無い kRO 新ログイン UI のうち自作した 7 ファイル（`bg_login.tga`、`bt_start_{normal,over,press}.bmp`、`bt_join_{normal,over,press}.bmp`）をコミットしています。生成スクリプトは `tools/scripts/make-login-overlay.ps1`（Phase 2 で `client/scripts/` へ移動予定）。手元の `bgi_temp.bmp` を分割した背景タイル `t_*.bmp` は jRO 由来のため `.gitignore` で除外してあり、未コミットです。

同じ内容の、ファイル名が文字化けしたディレクトリがもう 1 つ存在します。原因は未確認で、Phase 1 では触っていません。

## Config.local.js

`Config.js`（`window.ROConfigBase`）の既定値を `api.html` が deepMerge で上書きする設定です。境界パラメータ（ポート、PACKETVER、langtype 等）の表は [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) の所有物なのでここでは再掲しません。実ファイルの抜粋のみ載せます。

```js
window.ROConfigLocal = {
    remoteClient: 'http://127.0.0.1:8000/client/',
    servers: [
        {
            display: 'RO PreRE',
            address: '54.65.172.5',
            port: 6900,
            version: 55,
            langtype: 2,                 // japan -> shift-jis / CP932 for user-facing text
            packetver: 20211103,         // must match rAthena PACKETVER
            renewal: false,              // Pre-Renewal
            packetKeys: false,           // rAthena keys are 0 for > 2018-03-07
            socketProxy: 'ws://127.0.0.1:8000/',
            remoteClient: 'http://127.0.0.1:8000/client/',
            adminList: [2000000]         // クライアント UI 表示用。権限そのものはサーバの group
        }
    ],
    skipIntro: true,
    skipServerList: false,
    loadLua: false
};
```

全文は `client/robrowser/Config.local.js` です。アカウント（AID・グループ等）はサーバ管理者が発行します。本書には書きません。

## 文字コード

3 つの経路（GRF ファイル名 / テキストテーブル / ネットワーク）と、それぞれの文字コードの一覧表は [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) が所有します。ここでは、どのファイルで実装したかと、正規化ルールだけを書きます。

実装箇所（詳しい変更点は [`docs/PATCHES.md`](docs/PATCHES.md)）:

| ファイル | 役割 |
|---|---|
| `src/Utils/CodepageManager.js` | `networkCharset` / `setNetworkCharset` / `decodeNetwork` / `encodeNetwork` |
| `src/Utils/BinaryReader.js` | `getString()` を `decodeNetwork` 経由に |
| `src/Utils/BinaryWriter.js` | `setString`/`writeString` を `encodeNetwork` 経由に |
| `src/Engine/LoginEngine.js` | `langtype` から `setNetworkCharset` を呼ぶ（GRF 側の `setCharset` は呼ばない） |

送信時、IME が出しやすいが CP932 に無い Unicode 異体字を実在字へ正規化してからエンコードします: `U+301C`（波ダッシュ）→`U+FF5E`、`U+2016`→`U+2225`、`U+2212`（マイナス）→`U+FF0D`、`U+00A2`/`U+00A3`/`U+00AC` → 全角記号。固定長フィールドは文字境界で切り詰めます（マルチバイト文字の先頭バイトだけを送らない）。

修正前に作られたキャラクター「シアレス」は UTF-8 で保存されているため、文字コード試験の対象にしていません。

## キャラクター削除

PACKETVER `20211103` のパケット形式自体は変えていません。UI とサーバへの問い合わせ内容だけをこの運用に合わせています。

1. 削除予約 `0x0827`（キャラクター ID のみ）
2. 利用者が 8 桁の `YYYYMMDD` を入力する
3. 送信時に先頭 2 文字を除いた `YYMMDD`（6 バイト）を `0x0829` で送信する
4. サーバが `login.birthdate` と照合し、一致すれば削除する

6 桁だけ入力すると、送信時にさらに 2 文字削られて照合に失敗します。確認コードはクライアントに固定値として保存せず、自動入力・初期表示もしません。

旧 `msgstringtable` #19 は「登録メールアドレス」と表示しますが、この PACKETVER の削除フローはメールを使わないため、削除ダイアログの文言はクライアント側で差し替えています。不一致時の #1822 も、別の CSV が無関係な文言（`LIMITED`）で上書きしているため、クライアント側の日本語メッセージに差し替えています。実装の詳細は [`docs/PATCHES.md`](docs/PATCHES.md) の `CharEngine.js` / `CharSelectCommon.js` / `InputBox.js` を参照してください。サーバ側の照合仕様は `server/docs/SPEC.md`（統合予定パス）§7.5 です。

## スキル日本語化

`data/lua files/skillinfoz/skillnamelist.lub` と `skilldescript.lub`（Gravity の LuaP バイトコード）から文字列定数を直接抽出し、`SkillInfo.SkillName` と説明ウィンドウに反映しています（実装は `src/DB/DBManager.js`、詳細は [`docs/PATCHES.md`](docs/PATCHES.md)）。

- 説明の行頭にある `14^777777` のような数字（クライアント内部の行番号）は表示前に除去します。色指定 `^777777` は説明ウィンドウ側で色に変換されます。
- lub にスキルの説明が無い場合は `...` と表示されます。
- スキルツリー上のスキル名は、枠の都合で 7 文字で切れます。
- コンソールに `[skill-jp] applied display names:` と `[skill-jp] applied descriptions:` が出ます。
- レベル・SP・習得条件などの数値は内蔵テーブルのままです。`loadLua: true` にはしていません（`skillinfolist.lub` を読み込むと Pre-Renewal のレベル・SP まで上書きされるため）。

## ディレクトリ

```
client/
  README.md              このファイル。client の SoT
  robrowser/              実行コピー（ビルド成果物 + Config.local.js）
  clientdata/              GRF より優先する loose ファイル（自作ログイン UI を含む）
  data/                    ネイティブ exe 用の clientinfo.xml / sclientinfo.xml（roBrowser は読まない遺物）
  docs/
    GLUE.md                ro-glue の仕様（正本）
    PATCHES.md              上流からの差分 8 ファイル（正本）
    BUILD.md                再ビルド手順（正本）

tools/                    Phase 1 時点の実際の位置
  ro-glue/                 自作 glue。Phase 2 で client/ro-glue/ へ移動予定
  roBrowserLegacy-src/     クライアントソースの正本。Phase 2 で client/roBrowserLegacy-src/ へ移動予定
  scripts/                 GRF 調査・ログイン UI 生成スクリプト。Phase 2 で client/scripts/ へ移動予定
  node/                    Node.js 22 portable（未追跡）
```

## 起動手順

サーバは稼働中の前提です。`tools/ro-glue/` で glue を起動します（Windows 作業コピーの例では `<repo>` は `C:\RO-Lab` です）。

```powershell
cd <repo>\tools\ro-glue
node server.mjs --port 8000 `
  --static "<repo>\client\robrowser" `
  --grf "C:\Gravity\Ragnarok\data.grf" `
  --loose "<repo>\client\clientdata" --loose "C:\Gravity\Ragnarok" `
  --allow "54.65.172.5:6900,54.65.172.5:6121,54.65.172.5:5121" `
  --decrypt "<repo>\tools\roBrowserLegacy-src\src\Loaders\GameFileDecrypt.js"
```

起動したら Chrome で `http://127.0.0.1:8000/api.html?app=ONLINE` を開きます。CLI オプションの全一覧・既定値・エンドポイントは [`docs/GLUE.md`](docs/GLUE.md) を参照してください。

## 再ビルド

`src` を直したときの再ビルド手順は [`docs/BUILD.md`](docs/BUILD.md) にまとめています。

## 未対応

クライアント側のみを項目名で列挙します。状態（PASS/PARTIAL/TODO 等）と根拠は [`../docs/CURRENT_STATUS.md`](../docs/CURRENT_STATUS.md) を参照してください。

- 内蔵 UI の英語（職業名 `Novice` 等、スキル名内蔵表、メニュー HTML、`Disconnected from Server`、WorldMap の `Midgard` 等）
- lub にスキル説明が無いスキルの表示
- ネイティブ exe 化 / Electron 化
- `data.grf` の自動検出（現在は `--grf` 引数で明示指定）

## やらないこと

- jRO の `Ragexe.exe` を起動しない。
- GameGuard / Themida の回避、crack 済み exe、非公式ミラーからのクライアントや GRF の取得、第三者 RO サーバへの接続、資産の再配布をしない。
- `C:\Gravity\Ragnarok` へ書き込まない。
- パスワードをドキュメント、ログ、ソースから探さない。コードへ埋め込まない。
- `loadLua: true` にしない。`skillinfolist.lub` を読むと Pre-Renewal のレベルや SP まで上書きされる。
- ビルド済み `Online.js` を恒久的な修正箇所にしない。直すなら `tools/roBrowserLegacy-src/src/` を直し、[`docs/BUILD.md`](docs/BUILD.md) の手順で再生成する。`Config.local.js` はビルド成果物で上書きしない。
- サーバ側の変更が必要に見えても、クライアント作業では直さず Server-side Request として報告する。

## トラブルシューティング

- **文字化け**: 以前は CP932 の受信文字列を windows-1252 として表示していたのが原因でした（文字コードの節を参照）。修正後に再発した場合は `CodepageManager.js` / `LoginEngine.js` 周りを疑ってください。GRF 側（マップ名・アイテム名テーブル等）が化ける場合は原因が別（`userCharset`/`userCharpage`）です。
- **`Online.js` のキャッシュ**: Chrome は `Online.js`（約 12MB）をキャッシュします。再ビルド後に変更が反映されないときは、URL に `?v=` などのクエリを付けて再読み込みしてください。
- **glue が起動していない**: 資産が軒並み 404 になる、または画面が真っ黒のまま進まない場合は glue が起動しているか確認してください。`http://127.0.0.1:8000/__status` が応答すれば起動しています。
- **2 窓運用**: 別アカウントなら可。同一アカウントは後から開いた窓が先の接続を切ります。
