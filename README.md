# RO-Lab クライアント

作成日: 2026-09-24  
このファイルは、AI や後続作業者に「いま動いているクライアントは何か」を渡すための現行仕様です。

サーバ構築・Terraform・rAthena の運用手順はここには書きません。サーバ側の接続仕様の出典は `C:\RO-Lab\RO\RO\ro-server\CLIENT_HANDOFF.md` です。ただし HANDOFF はネイティブ RagexeRE を想定した記述が残っています。実際に起動しているのは、この README のブラウザクライアントです。

`notes\CLIENT_IMPLEMENTATION_SUMMARY.md`（2026-09-23）は途中経過です。スキル名、スキル説明、キャラクター削除 UI は載っていません。`notes\JAPANESE_CLIENT_TODO.md` は古いです。jRO の data.grf を読まない、とは書いてありますが、現行方針は手元の正規 data.grf を読み取り専用で使うことです。

---

## これは何か

Windows 上の Chrome で動く、rAthena Pre-Renewal 向けのブラウザクライアントです。公式の Ragexe.exe ではありません。

```
Chrome
  roBrowserLegacy（WebGL、GPL-3.0）
    Config.local.js
      packetver 20211103 / renewal false / langtype 2
        |
        | HTTP で資産、WebSocket でゲーム通信
        v
127.0.0.1:8000  ro-glue（自作、Node）
  静的配信   C:\RO-Lab\client\robrowser\
  GRF 配信   C:\Gravity\Ragnarok\data.grf（読み取り専用）
  loose      C:\RO-Lab\client\clientdata を GRF より優先
             C:\Gravity\Ragnarok も loose 参照（System / BGM など）
  WS → TCP   54.65.172.5:6900 / 6121 / 5121 だけ
        |
        | バイト列はそのまま。文字コード変換はしない
        v
AWS の rAthena Pre-Renewal（サーバは FREEZE。クライアントから変更しない）
  login 6900 / char 6121 / map 5121
  PACKETVER 20211103
  文字列は CP932
```

起動 URL は `http://127.0.0.1:8000/api.html?app=ONLINE` です。`index.html` はビューア用ランチャーなので、ゲーム本体ではありません。

別アカウントならブラウザを 2 窓開けます。窓ごとに WebSocket と TCP が 1 本ずつです。同じアカウントを 2 窓で使うと、後から入った方が先の接続を切ります。後ろに回した窓はブラウザが処理を間引くので、切断することがあります。

---

## 責務

### クライアント（roBrowserLegacy）がやること

- PACKETVER `20211103`、Pre-Renewal、`langtype 2` で login サーバへ接続する。
- ログイン、キャラクター選択・作成・削除、マップ入場、操作、描画を行う。
- 画面に出す文字列を、接続先の CP932 と jRO のクライアントデータに合わせる。
- パケットの中身（フォーマット、PACKETVER、難読化鍵）はサーバ仕様に合わせ、勝手に変えない。

### ro-glue がやること

- ビルド済みクライアントを `127.0.0.1` で配信する。
- `data.grf` と loose フォルダから、クライアントが要求したファイルを読む。GRF には書き込まない。
- ブラウザの WebSocket を、許可した 3 ポートへの TCP に中継する。中継時に文字コード変換やパケット改変はしない。
- 資産を `https://grf.robrowser.com/` など外へ取りに行かせない。`remoteClient` はローカル glue 固定。

### サーバがやること（クライアントでは直さない）

- アカウント認証、キャラクターの永続化、削除の可否、マップ上のルール、NPC の台詞、モンスター名、MOTD。
- キャラクター削除の照合。確認コードは `login.birthdate` と比較する。クライアントは値を保存しない。
- NPC が英語で話すのは、その NPC スクリプトが英語だからです。クライアントのテーブル不足ではありません。

サーバ側の変更が必要に見えても、クライアント作業では直さず、Server-side Request として報告します。

### やらないこと

- jRO の `Ragexe.exe` を起動しない。Themida と GameGuard があり、プロトコル系列もこのサーバと違います。
- GameGuard / Themida の回避、crack 済み exe、非公式ミラーからのクライアントや GRF の取得、第三者 RO サーバへの接続、資産の再配布をしない。
- `C:\Gravity\Ragnarok` へ書き込まない。
- パスワードをドキュメント、ログ、ソースから探さない。コードへ埋め込まない。
- `loadLua: true` にしない。`skillinfolist.lub` を読むと、Pre-Renewal のレベルや SP まで上書きされる。
- ビルド済み `Online.js` を恒久的な修正箇所にしない。直すなら `C:\RO-Lab\tools\roBrowserLegacy-src\src\` を直し、既存の build で再生成する。`Config.local.js` はビルド成果物で上書きしない。

---

## サーバに合わせている値

| 項目 | 値 |
|---|---|
| Login | `54.65.172.5:6900`。クライアントが最初に書く接続先はここだけ |
| Char / Map | `6121` / `5121`。ログイン後にサーバが通知する。glue の許可リストに入れて中継する |
| PACKETVER | `20211103` |
| モード | Pre-Renewal。`renewal: false` |
| version | `55`。サーバの version 検査は無効。接続可否には使わない |
| langtype | `2`（日本）。ネットワーク文字列は CP932 |
| パケット鍵 | `packetKeys: false`。サーバ鍵は `(0,0,0)` |
| キャラ名 | サーバ設定は日本語可、23 バイト |
| new_account / pincode | どちらも無効 |
| アカウント | `admin01`（AID 2000000、group 99）、`player01`（AID 2000001） |
| クライアント側 admin 表示 | `adminList: [2000000]`。これはクライアント UI 用。権限そのものはサーバの group |

rAthena commit は `e985006171d2eb320ee512a653f4c83aea3d81b6`。出典はサーバ資料。

---

## 文字コード

3 つを混ぜない。

| 経路 | 文字コード | 担当 |
|---|---|---|
| GRF 内のバイナリファイル名や一部リソース | `windows-1252`（`userCharset`） | クライアント。変えると GRF の日本語パスが壊れる |
| msgstringtable などテキストテーブル | langtype 2 から決まる `shift-jis`（実装上は CP932 と同じ変換表） | クライアント |
| ログイン、キャラ名、チャット、MOTD、NPC 台詞 | ネットワーク用 CP932。送受信とも UTF-8 ではない | クライアントの BinaryReader / BinaryWriter |
| glue | 変換しない | ro-glue |

文字化けの原因は、CP932 を windows-1252 として表示していたことでした。修正後、MOTD、新規日本語キャラ名、日本語チャットは通っています。修正前に作ったキャラクター「シアレス」は UTF-8 で保存されているので、文字コード試験の対象にしません。

---

## いま入っているクライアント側の日本語

`loadLua` は `false` のままです。

| 対象 | 状態 |
|---|---|
| GRF の msgstringtable、マップ名 | jRO データをそのまま表示。日本語 |
| スキル名 | `data/lua files/skillinfoz/skillnamelist.lub` の表示名だけを `SkillInfo.SkillName` に載せる |
| スキル説明 | `data/lua files/skillinfoz/skilldescript.lub` の本文を説明ウィンドウへ渡す |
| 職業名、メニュー、ステータス欄などの内蔵 UI | 英語のまま。未対応 |
| スキルのレベル、SP、習得条件の数値 | 内蔵テーブルのまま。lub では上書きしない |
| NPC 台詞 | サーバが送った文字列。クライアントテーブルではない |

`skillnamelist.lub` と `skilldescript.lub` は Gravity の LuaP バイトコードです。同梱の Lua 5.1 では実行できないので、ファイル内の文字列定数を読んで対応付けています。説明の行頭にある `14^777777` のような数字はクライアント内部の行番号なので、表示前に外しています。色指定 `^777777` は説明ウィンドウが色に変えます。lub に無いスキルの説明は `...` です。

コンソールに `[skill-jp] applied display names:` と `[skill-jp] applied descriptions:` が出ます。スキルツリーの名前は、枠の都合で 7 文字で切れます。

---

## キャラクター削除

PACKETVER `20211103` の流れです。パケット形式は変えていません。

1. 削除予約 `0x0827`（キャラクター ID のみ）
2. 利用者が確認コードを入力する
3. 削除確定 `0x0829`
4. サーバが `login.birthdate` と照合し、一致すれば正規の削除処理を行う

画面に入れるのは 8 桁の `YYYYMMDD` です。送信時に先頭 2 文字を除き、packet の 6 バイトは `YYMMDD` です。6 桁だけ入れると、さらに 2 文字削れて照合に失敗します。

確認コードはクライアントに固定値として入れません。自動入力、初期表示、サーバからの取得、ローカル保存もしません。アカウント作成時の birthdate は変わり得るため、利用者の入力を送るだけです。

古い msgstringtable #19 は「登録メールアドレス」と出します。この PACKETVER の削除はメールを使わないので、削除ダイアログの文言だけクライアント側で差し替えています。不一致時の #1822 は、別の CSV が `LIMITED` で上書きしているため、不一致メッセージもクライアント側の日本語にしています。

---

## ディレクトリ

```
C:\RO-Lab\
  README.md                 このファイル。クライアントの現行仕様
  RO\RO\ro-server\          サーバ資料。読むだけ
  tools\
    node\                   Node.js 22 portable。システムの PATH は変えていない
    roBrowserLegacy-src\    クライアントソース。修正の正本。commit e43b9b2 から分岐
    ro-glue\                自作 glue。server.mjs
    scripts\                GRF 調査、ログイン画面の不足画像を作るスクリプト
  client\
    robrowser\              実行コピー。Online.js と Config.local.js
    clientdata\             GRF より優先する loose ファイル。自作ログイン UI を含む
  notes\                    調査メモ。現行仕様は本 README を優先する
  backup\                   過去ビルドの退避

C:\Gravity\Ragnarok\        jRO 公式インストール。読み取り専用
  data.grf                  使う
  Ragexe.exe                使わない
```

ソースの正本は `tools\roBrowserLegacy-src\src\` です。再ビルドは、そのディレクトリで次を実行します。

```powershell
$env:PATH = "C:\RO-Lab\tools\node;" + $env:PATH
node ./applications/tools/builder-web.mjs -O
```

生成された `dist\Web\Online.js`、`ThreadEventHandler.js`、`PathFindingWorker.js` を `client\robrowser\` へコピーします。`Config.local.js` はコピーしません。ブラウザは `Online.js` をキャッシュするので、反映には再読み込みが必要です。

glue の起動例:

```powershell
cd C:\RO-Lab\tools\ro-glue
C:\RO-Lab\tools\node\node.exe server.mjs --port 8000 `
  --static "C:\RO-Lab\client\robrowser" `
  --grf "C:\Gravity\Ragnarok\data.grf" `
  --loose "C:\RO-Lab\client\clientdata" --loose "C:\Gravity\Ragnarok" `
  --allow "54.65.172.5:6900,54.65.172.5:6121,54.65.172.5:5121" `
  --decrypt "C:\RO-Lab\tools\roBrowserLegacy-src\src\Loaders\GameFileDecrypt.js"
```

`--dump-rx` を付ける場合、ダンプするのはサーバからクライアントへのバイトだけです。パスワードを含むクライアント送信はダンプしません。

GRF 内エントリの DES 復号は、exe の保護解除ではなく、GRF 形式を読むための処理です。roBrowserLegacy 同梱の `GameFileDecrypt.js` を glue が import しています。

---

## 未対応

- 職業名、基本ステータス、インベントリ見出しなど、プログラムに埋め込まれた英語 UI。
- スキル説明のうち、lub に行が無いもの。
- サーバスクリプトが英語の NPC（例: 初心者修練場の Shion）。これはサーバ側の仕事です。
- ネイティブ exe としての起動。いまは Chrome です。将来やるなら Chrome のアプリモードか Electron であり、Ragexe.exe の代替バイナリではありません。
