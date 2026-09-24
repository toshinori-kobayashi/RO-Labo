# クライアント接続手順書（rAthena Pre-Renewal 検証サーバ）

> **HISTORICAL（2026-09-24）** — この文書は kRO 2021-11-03 RagexeRE ネイティブクライアント + WARP + clientinfo.xml を前提に書かれています。実際に稼働しているクライアントは roBrowserLegacy + ro-glue（RO-Labo リポジトリ `client/README.md`）で、この前提は当てはまりません。サーバ側の現行値は [../../server/docs/SPEC.md](../../server/docs/SPEC.md) §6〜§9、実クライアントは [../../client/README.md](../../client/README.md) を参照してください。2026-09-24 に RO-Labo の `notes/archive/` へ移動済み。

この文書だけでクライアント側の接続作業を開始できます。サーバ側の構築・運用については触れません（必要な場合は SRE に確認してください）。

認証情報（アカウント ID / パスワード）はこの文書には記載しません。SRE から別経路で受け取ってください。

## サーバ接続情報

| 項目 | 値 |
|---|---|
| Public IP | `54.65.172.5` |
| Public DNS | `ec2-54-65-172-5.ap-northeast-1.compute.amazonaws.com` |
| Login Server（クライアントが直接接続する唯一のサーバ） | `54.65.172.5` : `6900` |
| Char Server（ログイン後にサーバから通知される） | `54.65.172.5` : `6121` |
| Map Server（キャラ選択後にサーバから通知される） | `54.65.172.5` : `5121` |
| PACKETVER | `20211103` |
| rAthena commit | `e985006171d2eb320ee512a653f4c83aea3d81b6`（master、2026-08-21） |
| 動作モード | **Pre-Renewal**（1 次職・2 次職・転生まで実装。**3 次職はありません**） |

補足: RO クライアントは `clientinfo.xml` に **login server の情報のみ**を書きます。char-server / map-server のアドレスは、ログイン成功後にサーバ側から動的に通知されます（本サーバではどちらも Public IP を通知するよう設定済みです）。char/map のポートは疎通確認やファイアウォール確認のために把握しておいてください。

## `clientinfo.xml` の例

### 段階 1: 初回接続用の最小構成（ASCII のみ。まずこれでログインまで確認する）

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

保存時の注意: **BOM なし**で保存する（Cursor / VS Code は既定で BOM なし。ステータスバーの `UTF-8 with BOM` を避ける）。段階 1 は ASCII のみなので UTF-8 / Shift_JIS のどちらで保存しても同じバイト列になる。

### 要素の意味と根拠

| 要素 | 置く場所 | 必須 | 説明 |
|---|---|---|---|
| `<servicetype>` | `<clientinfo>` 直下 | **必須** | クライアントの地域設定。`japan` で文字コード CP932・フォント charset SHIFTJIS になる。無いと `No ServiceType !!` エラー |
| `<servertype>` | `<clientinfo>` 直下 | **必須** | 有効値は `primary` / `sakray` / `local` / `pk` のみ。それ以外（例: `RO`）は `ServerType Error !!` になる。rAthena wiki の推奨に従い `sakray` |
| `<address>` / `<port>` | `<connection>` 内 | 必須 | login-server の Public IP `54.65.172.5` と `6900` |
| `<version>` | `<connection>` 内 | 必須 | ログイン時に申告する値。サーバ側 `check_client_version` は無効（rAthena 既定）なので接続可否には影響しない。慣例値 `55` |
| `<langtype>` | `<connection>` 内 | 必須（日本語表示のため） | `2` = japan。内部的には `<servicetype>` と同じ変数を上書きする（後述） |
| `<display>` | `<connection>` 内 | 必須（サーバ選択画面の表示名） | 段階 1 では ASCII |
| `<desc>` / `<balloon>` | `<connection>` 内 | 任意 | 説明とツールチップ。段階 1 では ASCII |

`<servicetype>` と `<langtype>` の関係（クライアント再構築ソース `Framework/Locale.cpp` の処理順から確認）:

1. 起動時に `<clientinfo>` 直下の `<servicetype>` / `<servertype>` を読む（`SetOption`）。
2. 次に先頭の `<connection>` を読み、その中に `<servicetype>` があれば上書き、続いて `<address>` `<port>` `<version>` を読み、**最後に `<langtype>` で同じ内部変数を上書き**する（`SelectClientInfo`）。
3. 各要素は名前で検索されるため、**XML 内で先に書くか後に書くかは無関係**。両方指定した場合は常に `<langtype>` が優先される。したがって `<servicetype>japan</servicetype>`（root、必須）+ `<langtype>2</langtype>`（connection 内）の組み合わせが正しい。

上記は 2010 年世代クライアントの再構築ソースと rAthena wiki のサンプル（`servicetype` は root、`langtype` は connection 内）に基づく。**2021-11-03 RagexeRE 実機での動作は未確認**だが、WARP の LangType 検出も同じ `SetOption` 内の文字列比較を前提にしており、構造は維持されていると判断している。

### XML 宣言の `encoding` について

- クライアントの XML パーサは `<?xml ... ?>` 行を読み飛ばすだけで、`encoding` 属性を解釈しない（再構築ソース `Base/Xml.cpp`: `<?` で始まるタグは終了タグ扱いで無視、文字コード変換処理なし）。ファイルの**バイト列がそのまま**使われ、画面表示時に `langtype` の codepage（`2` なら CP932）で解釈される。
- つまり「XML 宣言の encoding」と「langtype=2 の CP932」は別概念で、前者は実質的に飾り。慣例の `encoding="euc-kr"` を残しても害はない（rAthena wiki のサンプルどおり）。
- 日本語文字列を入れる場合に効くのは**ファイル自体を Shift_JIS（CP932）で保存すること**。UTF-8 のまま日本語を書くとサーバ選択画面で文字化けする。この挙動は 2021 実機で未確認のため、段階 1 は ASCII のみにしている。

### 段階 2: 接続成功後に追加する任意要素

段階 1 でログイン〜キャラクター選択まで通ったら、必要に応じて以下を追加する。1 つずつ足して切り分けること。

```xml
<?xml version="1.0" encoding="Shift_JIS" ?>
<clientinfo>
    <servicetype>japan</servicetype>
    <servertype>sakray</servertype>
    <extendedslot />
    <readfolder />
    <connection>
        <display>検証サーバ</display>
        <desc>Pre-Renewal 検証サーバ</desc>
        <balloon>EXP x10 / Drop x5 / Card x100</balloon>
        <address>54.65.172.5</address>
        <port>6900</port>
        <version>55</version>
        <langtype>2</langtype>
        <registrationweb></registrationweb>
        <aid>
            <admin>2000000</admin>
        </aid>
        <loading>
            <image>loading00.jpg</image>
            <image>loading01.jpg</image>
        </loading>
    </connection>
</clientinfo>
```

| 要素 | 意味 | 注意 |
|---|---|---|
| 日本語の `<display>` / `<desc>` | サーバ選択画面の日本語表示 | ファイルを **Shift_JIS で保存**（Cursor: 右下のエンコーディング → "Save with Encoding" → Japanese (Shift JIS)）。宣言の `encoding` は合わせて `Shift_JIS` にしておくと編集時に混乱しない（クライアントは読まない） |
| `<extendedslot />` | 全キャラクタースロットを有効化 | 任意 |
| `<readfolder />` | GRF より `data/` フォルダを優先 | WARP の "Read Data Folder First" と同じ目的。どちらか一方でよい |
| `<registrationweb>` | 登録ボタンの URL | 使わないので空か省略 |
| `<aid><admin>` | クライアント側の GM 表示（GM スプライト・右クリックメニュー）を有効にする account_id | サーバ側の GM 権限とは独立。`2000000` は本サーバの GM アカウント `admin01` の実際の account_id |
| `<loading>` | ローディング画像 | `data/texture/유저인터페이스/` 配下に画像が必要。無い画像を書くと表示が乱れるので、用意した分だけ書く |
| `<passwordencrypt />` / `<passwordencrypt2 />` | パスワードのクライアント側暗号化 | **使わない**（本サーバは平文ログイン前提） |
| `<hideaccountlist />` | サーバ選択画面を省略 | 段階 1 では付けない（切り分けのため） |

## 想定クライアント世代

**kRO 2021-11-03 RagexeRE** 系のクライアントを想定しています（rAthena の PACKETVER 20211103 に対応する世代）。

- **jRO（ガンホー運営の日本公式サービス）のクライアントは使用できません。** rAthena のパケットテーブルは kRO の Ragexe / RagexeRE 系譜のみに対応しており、jRO クライアントのパケット構成には対応していません。日本語化は kRO クライアント + 日本語データ（後述）で行います。
- 2018-03-07 以降にリリースされたクライアントはパケット暗号化が無効（キー 0）になっているため、本サーバでは "Disable Packet Encryption" 系のパッチは不要です。

## langtype / servicetype の想定

- `langtype 2`（`servicetype japan` と同じ内部値）を指定すると、クライアントは文字コードを **CP932**、フォントの charset を **SHIFTJIS_CHARSET** に設定します。日本語表示にはこの設定が必須です。
- `<servicetype>` は `<clientinfo>` 直下（必須）、`<langtype>` は `<connection>` 内に書きます。両者は同じ内部変数に入り、クライアントの処理順で `<langtype>` が最後に代入されるため **`<langtype>` が常に優先**されます。XML 内の記述順は関係ありません。

## WARP パッチについて

WARP（クライアント改造ツール）を使う場合の要否です。

**必要:**

- Disable 1rag1/1sak1 type parameters
- Read Data Folder First または Enable Multiple GRFs
- Always load Korea ExternalSettings lua file（`langtype` が 0 以外の場合、`service_korea` の設定しか存在しないため必要になる可能性が高い）
- Always Call SelectKoreaClientInfo()
- Disable filename check（実行ファイル名を変更する場合）
- Customize Font name（MS ゴシック / メイリオ等、日本語フォントを指定）

**不要:**

- Always read msgstringtable.txt / Use plain text descriptions（`langtype` が 0 以外なら既定の動作）
- Disable Packet Encryption（2018-03-07 以降のクライアントではもともと無効）

**最初は当てないこと:**

- Use Ascii on All LangTypes（マルチバイト判定を無効化するパッチ。日本語チャットの BackSpace 等に副作用の疑いがあり未検証。表示・入力に問題が出た場合の切り分け用に温存してください）

## 疎通確認方法

Mac / Linux:

```sh
nc -zv 54.65.172.5 6900
nc -zv 54.65.172.5 6121
nc -zv 54.65.172.5 5121
```

Windows（PowerShell）:

```powershell
Test-NetConnection -ComputerName 54.65.172.5 -Port 6900
Test-NetConnection -ComputerName 54.65.172.5 -Port 6121
Test-NetConnection -ComputerName 54.65.172.5 -Port 5121
```

いずれも `TcpTestSucceeded : True`（または `nc` が接続に成功して即座に終了）であれば OK です。22 番・3306 番は意図的に公開していないため、接続できなくて正常です。

期待される動作: クライアント起動 → サーバ選択画面に `clientinfo.xml` の `<display>` の名前が出る → 選択するとログイン画面へ進む（アカウント未取得の間はログイン自体は失敗します）。サーバ選択画面にすら進まない場合は `clientinfo.xml` の設定ミスかポート到達性の問題です。

## 接続に失敗したときに確認するサーバログ

問題が起きた段階によって、確認すべきログが異なります。

| 段階 | 確認するサーバ | 見るべき内容 |
|---|---|---|
| ログイン認証で弾かれる | login-server | ID/パスワードの照合結果、BAN 状態 |
| キャラクター選択画面に進めない | char-server | char-server への接続結果、`char_ip` の応答 |
| キャラクター選択後・マップ移動でエラー | map-server | map-server への接続結果、マップ読み込み |

ログの取得方法:

- CloudWatch Logs からの取得は **SRE に依頼**してください（`scripts/logs.sh` はローカル Mac の AWS 認証情報が必要な SRE 向けツールです）。
- クライアント担当自身が `scripts/logs.sh` を使える場合（SRE と同じ AWS 権限を持つ場合）は次のように使えます。

  ```sh
  scripts/logs.sh login-server --since 30m
  scripts/logs.sh char-server --since 30m
  scripts/logs.sh map-server --follow
  ```

## クライアント側で一致させる必要がある設定

| 設定 | サーバ側の値 | 備考 |
|---|---|---|
| PACKETVER / クライアント exe の日付 | `20211103`（kRO 2021-11-03 RagexeRE） | 異なる世代の exe だとパケット不整合で接続できない、または不具合が出ます |
| langtype | `2` | 日本語表示に必須 |
| パケット暗号化 | 無効（サーバ側もキー 0） | 2018-03-07 以降の exe であれば追加設定不要 |
| ポート | login 6900 / char 6121 / map 5121 | clientinfo.xml に書くのは login のみ |
| キャラクター削除の確認コード | `char_del_option: 2`（生年月日）、`char_del_delay: 0`（待ち時間なし） | 削除確認では **生年月日 `YYYYMMDD`** を入力します（SRE がアカウント発行時に伝える値。既定は `20000101`）。詳細は下記「キャラクター削除」 |

## アカウントの発行

アカウントは SRE が `create-account.sh` を使って作成します。ID・パスワードは Slack DM やパスワード共有ツールなど、この手順書とは別の経路で受け取ってください。GM 権限（group_id 99）が必要な場合は SRE にその旨を伝えてください。

## キャラクター削除

PACKETVER 20211103 のクライアントは、キャラクター削除を「削除予約（0x0827）→ 生年月日 `YYMMDD` で確定（0x0829）」の 2 段階で行います。サーバは `login.birthdate` と照合します。

- 入力する値は **生年月日 `YYYYMMDD`**（アカウント発行時に SRE が伝えます。既定は `20000101`）。メールアドレスではありません。
- roBrowserLegacy では最初の確認ダイアログの文言が msgstringtable #19「削除するには、登録メールアドレスを入力してください」のままですが（クライアントの旧文言）、続いて出るテキストボックスは生年月日入力（msgstringtable #1815）で、入力した 8 桁のうち下 6 桁がサーバへ送られます。文言だけの問題で、サーバ設定では変えられません。
- 生年月日が違うと「生年月日が一致しません」相当（result 5）で拒否されます。パーティ / ギルド所属中のキャラクターは削除できません（`char_del_restriction: 3`）。
- 待ち時間は 0 に設定してあるため、予約直後にそのまま確定できます。

## サーバ側の既定値・制約（クライアント担当が知っておくべきこと）

| 項目 | サーバ側の状態 | クライアントへの影響 |
|---|---|---|
| PIN コード | `pincode_enabled: no` | キャラクター選択前の PIN 入力は出ません |
| 新規アカウント登録 | `new_account: no`（`_M` / `_F` 登録無効） | アカウントは SRE が発行します。ID 末尾に `_M`/`_F` を付けても登録されません |
| パケット暗号化 | 無効（キー 0） | 追加パッチ不要 |
| web-server（HTTP 8888） | **起動していません** | ギルドエンブレムの表示・アップロード、冒険者アカデミー等の HTTP API を使う機能は動作しません。ログイン・プレイには影響しません |
| キャラクター名 / ギルド名 / パーティ名 | 日本語可、全角 11 文字（23 バイト）まで、最小 4 バイト、禁止記号 `!"#$%&'()*+,/:;<=>?` | 制限を超える名前は作成に失敗します |
| パスワード保存 | `use_MD5_passwords: no` | クライアント側の設定変更は不要 |
| GM コマンドの応答メッセージ | 英語 | `@` コマンドを使う GM 検証では英語表示になります |

---

## Japanese Client Requirements

日本語クライアントを準備する担当者向けの技術要件です。

### 推奨 clientinfo.xml 設定

- `servicetype`: `japan`（`<clientinfo>` 直下、必須）
- `servertype`: `sakray`（`<clientinfo>` 直下、必須。有効値は primary / sakray / local / pk）
- `langtype`: `2`（`<connection>` 内。`servicetype` より優先される。記述順は無関係）
- 想定 encoding: **CP932**（クライアントが解釈する文字コード）
- `PACKETVER`: `20211103`
- 想定クライアント世代: **kRO 2021-11-03 RagexeRE**

### 日本語表示に必要なクライアント側データ（CP932 で用意）

以下はすべてクライアント側が持つデータで、サーバからは提供されません。

- `data/msgstringtable.txt`
- `data/mapnametable.txt`
- `data/questid2display.txt`
- `data/cardprefixnametable.txt`
- `data/luafiles514/lua files/datainfo/*`（itemInfo。アイテム名・説明）
- `data/luafiles514/lua files/skillinfoz/*`（スキル名・説明）
- `UI\` 配下の画像リソース

**jRO 公式データの流用は権利確認が必要です。** 本プロジェクトの調査では、rAthena 向けにライセンスが明確な日本語 NPC 翻訳データは見つかっていません（詳細は `docs/DESIGN.md` §10.5）。クライアント側データも同様に出所と利用条件を確認してから使用してください。

### Item / Skill / Mob 等の表示データの所在

| 種別 | 所在 |
|---|---|
| Item 名・説明 | **クライアント**（`datainfo` の itemInfo） |
| Skill 名・説明 | **クライアント**（`skillinfoz`） |
| Map 名 | **クライアント**（`mapnametable.txt`） |
| Quest 名・本文・Quest UI | **クライアント**（`questid2display.txt`） |
| Mob 名 | **サーバ**（`mob_db` の `JapaneseName`。クライアント側の対応は不要） |

Mob 名だけはサーバから送信されるため、クライアント側のデータ有無に関わらず、討伐対象名を含めて日本語で表示されます（サーバ側で対応済みの Mob に限る。後述）。

### Font

`langtype 2` では文字コードの charset は **SHIFTJIS 固定**です。フォントの見た目（フェイス）は WARP の "Customize Font name" で MS ゴシック / メイリオ等を指定してください。

### 日本語 Chat の可否

サーバはチャット文字列をバイト列として透過するだけなので、クライアントが CP932 で送信すれば日本語チャットはサーバ側では問題なく成立します。ただし **クライアントの IME による日本語入力が実機で正しく動作するかは未検証**です。実機で確認してください。"Use Ascii on All LangTypes" パッチは（前述のとおり）最初は当てないでください。

### 日本語 Character Name の可否

- **サーバ側は許可済み**です（`char_name_option: 2` の禁止リスト方式）。
- 最大長: 全角 **11 文字**（`NAME_LENGTH` の制約により 23 バイトまで、全角 1 文字 = 2 バイト）。
- 最小長: 全角 **2 文字**（4 バイト、rAthena 既定値）。
- 禁止記号: `!"#$%&'()*+,/:;<=>?`（半角スペースも実質使用不可）。
- **クライアントの作成 UI で日本語（IME）入力ができることを実機で確認済み**です（2026-09-24、「シアレス」を作成）。

### 日本語 Guild / Party Name の可否

キャラクター名と同じ制約（サーバ側許可・全角 11 文字まで・同じ禁止記号）です。クライアント UI での入力可否も同様に未検証です。

### サーバ側で既に日本語化済みの範囲

以下はサーバ側の対応が完了しています。

- NPC 会話・案内・転職・クエスト等 148 ファイル分（カプラ機能・カプラ NPC、各都市の案内 NPC、1 次職転職 NPC 6 種、二次職転職クエスト、プラチナスキルクエスト、初期都市クエスト 等）
- NPC の頭上表示名（可視 NPC 1,108 体中 1,099 体を日本語化。`日本語#suffix::旧フル名` 方式のため NPC の内部識別子（exname）自体は変わらない）
- 独自 NPC 2 体: 「サポート職員」（プロンテラ 160,180。全回復・主要都市への無料ワープ・サーバ説明）、「冒険者支援員」（初心者修練場をスキップして一次職へ即時転職。詳細は次節「初心者修練場スキップ NPC」）
- Mob 名（215 種のカタカナ表記。未収録 Mob は英語のまま）
- サーバメッセージ 214 件（GM コマンドの応答は英語のまま）
- MOTD（ログイン時のお知らせ）

**上記以外の NPC はすべて英語のままです。** 未翻訳範囲（フェイヨン系クエスト、転職導線の残り、日常 NPC 小物、Ep.10 以降の街クエスト 等）は `docs/JP_NPC_PLAN.md` を参照してください。追加の日本語化はサーバ側の作業（SRE への依頼）が必要です。

### 初心者修練場スキップ NPC（冒険者支援員）

初心者修練場（new_1-1〜new_5-1、出現地点のすぐ東）に「冒険者支援員」という独自 NPC がいます。Novice（一次職に就く前のキャラクター）がこの NPC に話しかけると、修練場を最後まで進めなくても一次職 6 職（剣士 / アーチャー / マジシャン / アコライト / 商人 / シーフ）のいずれかへ即座に転職できます。

- **使い方**: Novice の状態で「冒険者支援員」に話しかける → 転職したい一次職を選ぶ（辞退・キャンセルも可）→ 全回復とノービスポーション 10 個が付与され、プロンテラへワープします。
- 転職後のステータスは通常どおり修練場をクリアして転職した場合と同じです（JobLv 1 / JobExp 0 / Basic Skill 習得済み）。
- 既に一次職以上のキャラクターがこの NPC に話しかけると「すでに職業についているため、このサービスは利用できません。」と表示され、利用できません。

### クライアント側で日本語化する必要がある範囲

上記「サーバ側で既に日本語化済みの範囲」に含まれないものは、原則としてクライアント側のデータ（`msgstringtable.txt` 等、前述のファイル群）を用意しない限り英語表示のままです。特に Item / Skill / Quest UI / Map 名はサーバからは一切日本語化できません。

### 文字化け発生時の切り分け方法

順番に確認してください。

1. DB に正しい日本語が保存されているか（SRE に `scripts/list-accounts.sh` 等での確認を依頼）→ 正しければサーバ〜DB 間は正常。
2. CloudWatch の map-server ログで NPC 名が正しく読めるか（SRE に確認を依頼）→ 読めればサーバ側の CP932 変換経路は正常。
3. クライアントの `langtype` が `2` になっているか、フォントが日本語対応か。
4. クライアントの `data` ファイルが CP932 で保存されているか（UTF-8 のまま配置すると化けます）。
5. 特定の文字だけ `?` に化ける場合、その文字は CP932 に存在しない（変換不能な）文字です。使用を避けてください。

### 検証チェックリスト

以下の順に確認することを推奨します（表示が崩れた状態でチャット等を検証しても切り分けが難しくなるため）。

1. **表示** — サーバ選択画面、ログイン、NPC 会話（カプラ・サポート職員等）、Mob 名が正しく日本語表示されるか
2. **チャット** — 日本語入力・送信・他プレイヤーへの表示が正しいか（IME 含む）
3. **キャラクター名** — 確認済み（2026-09-24）。作成 UI で日本語キャラ名を入力・登録できることを実機で確認（「シアレス」を作成）
4. **ギルド名 / パーティ名** — 同上（未検証）
5. **キャラクター削除** — 確認済み（2026-09-24）。キャラクター選択画面から削除し、確認入力に生年月日 `YYYYMMDD` を入れて、日本語名のキャラクター（「ユンヌ」）を削除できることを実機で確認

---

## クライアント担当が最初にやること

1. 本書の「疎通確認方法」に従い、`54.65.172.5` の 6900 / 6121 / 5121 番ポートへの到達性を確認する。
2. 「日本語表示に必要なクライアント側データ」に記載の CP932 データ（`msgstringtable.txt` 等）を用意する。出所と利用条件（特に jRO データの流用可否）を事前に確認する。
3. 本書「段階 1: 初回接続用の最小構成」の `clientinfo.xml`（ASCII のみ、`servicetype`/`servertype` は root、`address` `54.65.172.5`・`port` `6900`・`version` `55`・`langtype` `2`）を **そのまま** BOM なしで配置する。日本語の表示名や loading 画像はこの時点では入れない。
4. 必要な WARP パッチ（本書「WARP パッチについて」の「必要」欄）を適用する。「最初は当てないこと」に挙げたパッチは適用しない。
5. SRE に一般アカウント（および必要なら GM アカウント）の払い出しを依頼する。
6. サーバ選択画面 → ログイン → キャラクター選択までの疎通を確認する。通ったら「段階 2」の任意要素（日本語表示名は Shift_JIS 保存）を 1 つずつ追加して再確認する。
7. 「検証チェックリスト」の順（表示 → チャット → キャラ名 → ギルド名）で日本語対応状況を確認し、問題があれば「文字化け発生時の切り分け方法」に沿って原因を特定する。
