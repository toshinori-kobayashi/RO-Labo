# 上流 roBrowserLegacy からの差分

`tools/roBrowserLegacy-src/`（Phase 2 で `client/roBrowserLegacy-src/` へ移動予定）は上流 [MrAntares/roBrowserLegacy](https://github.com/MrAntares/roBrowserLegacy) の全コピーです。基準コミットは `e43b9b2bded117b945ebfd3d7604042546ca5354`。このコミットとの差分は `diff -rq` で確認した次の 8 ファイルだけです（本書は `diff -u` で実際の差分を読んで書いています）。`tools/roBrowserLegacy-src/AGENTS.md` `REVIEW.md` `DOCKER.md` は上流のファイルであり、本プロジェクトの指示ではありません。

**修正の正本は `src` です。ビルド成果物の `Online.js` を直接編集しないでください。** 上流を更新するときは、この 8 ファイルの変更をコミットの先頭から読み直して再適用してください（マージではなく作り直しが安全です）。再ビルド手順は [`BUILD.md`](BUILD.md)。

GPL の要件である「改変ファイルへの改変の事実と日付の表示」は、現状 `src` 内のファイルヘッダに入っていません。Phase 2/3 で各ファイルの先頭コメントに追記予定です。

---

## 1. `src/Utils/CodepageManager.js`

**目的**: ネットワーク（パケット）文字コードを、GRF/DB 文字コード（`userCharset`）から分離するための土台を追加する。

**要点**:
- `networkCharset` フィールド（既定値 `windows-1252`）を追加。
- `setNetworkCharset(charset)` — `iconv-lite` に存在する charset 名かを確認してから `networkCharset` を差し替える。
- `decodeNetwork(data)` — `Uint8Array` を受け取り、`smartDecode(data, networkCharset)`（UTF-8 を先に試し、不正なら `networkCharset`）でデコードする。
- `encodeNetwork(str, maxBytes)` — `networkCharset` が CP932 系（`shift-jis` / `sjis` / `windows-932` / `cp932` 等）の場合、送信前に IME 由来の Unicode 異体字を CP932 側の実在字へ正規化してからエンコードする（波ダッシュ U+301C→全角チルダ U+FF5E、U+2016→U+2225、マイナス U+2212→全角ハイフンマイナス U+FF0D、¢£¬ → 全角記号）。`maxBytes` 指定時は、バイト数超過分を **文字単位**で末尾から落とす（マルチバイト文字の先頭バイトだけを送らないため）。

**依存関係**: `BinaryReader.js` / `BinaryWriter.js` がそれぞれ `decodeNetwork` / `encodeNetwork` を呼ぶ。`LoginEngine.js` が `setNetworkCharset` を呼んで初期値を決める。

---

## 2. `src/Utils/BinaryReader.js`

**目的**: パケットから読む文字列をネットワーク文字コードでデコードする。

**要点**: `getString()` 内の `TextEncoding.decode(bytes, 'utf-8')` 固定呼び出しを `TextEncoding.decodeNetwork(bytes)` に変更。マップの `.gat` やスキル内部名など、charset 変換をしてはいけないバイト列を読む `readBinaryString()` は変更していない（GRF ローダはこちらを使うため影響しない）。

**依存関係**: `CodepageManager.decodeNetwork`。

---

## 3. `src/Utils/BinaryWriter.js`

**目的**: パケットへ書く文字列をネットワーク文字コードでエンコードする。

**要点**: `DataView.prototype.setString` と `BinaryWriter.prototype.setString`/`writeString` の両方で、`TextEncoding.encode(str, 'utf-8')` 固定呼び出しを `TextEncoding.encodeNetwork(str, len)` に変更。固定長フィールドは、文字コード変換後にバイト数が足りない分を `0` 埋めする（`i < data.length ? data[i] : 0`）。可変長フィールドで、マルチバイト化によりエンコード後のバイト数が `str.length` を超える場合にバッファを再確保するロジック（上流にもあった）はそのまま維持している。

**依存関係**: `CodepageManager.encodeNetwork`。

---

## 4. `src/Engine/LoginEngine.js`

**目的**: サーバの `langtype` からネットワーク文字コードを決定し、`CodepageManager` に設定する。GRF 側の文字コードは触らない。

**要点**: 上流は `TextEncoding.detectEncodingByLangtype(...)` の結果を GRF 用の `setCharset()` に渡していたが、これを `TextEncoding.setNetworkCharset(charset)` に渡すよう変更。`Configs.get('networkCharset')` が設定されていればそちらを優先する（`langtype` 判定より明示指定が勝つ）。コンソールログも `[LOGIN] Network Encoding:`（ネットワーク文字コード）と `[LOGIN] GRF Encoding:`（`TextEncoding.userCharset`）の 2 行に分けて、どちらが何の文字コードか分かるようにした。

**依存関係**: `CodepageManager.setNetworkCharset`。

---

## 5. `src/DB/DBManager.js`（skill-jp）

**目的**: jRO 手元データの `skillnamelist.lub` / `skilldescript.lub` からスキルの表示名・説明を抽出し、`SkillInfo[].SkillName` と説明ウィンドウ用の `SkillDescription[]` に上書きする（日本語化。スキル名・説明の詳細な挙動は [`../README.md`](../README.md) の該当節を参照）。

**要点**: DB ロードチェーンに `loadSkillDisplayNames()` / `loadSkillDescriptions()` を追加。両ファイルは Gravity の LuaP バイトコードで、同梱の Lua 5.1 では実行できないため、**バイト列から長さプレフィックス付き文字列定数を直接スキャンして**取り出す（`applySkillDisplayNames` / `applySkillDescriptions`）。名前は SKID 定数トークンの直後に現れる非ラベル文字列を採用し、説明は SKID トークン以降の行を改行区切りで連結したうえで、行頭の `14^777777` のような番号（クライアント内部の行 ID）を取り除く。スキルのレベル・SP・習得条件など数値側のテーブルはここでは変更しない。

**依存関係**: `SKID` 定数テーブル、`userStringDecoder` / `userCharpage`（GRF 側の文字コード。ネットワーク文字コードとは別）。

---

## 6. `src/Engine/CharEngine.js`

**目的**: PACKETVER 20211103 のキャラクター削除確認 UI を、このサーバー運用（生年月日照合方式）に合わせて差し替える。

**要点**: 削除確認ダイアログの文言を、上流の `DB.getMessage(19)`（msgstringtable 由来「登録メールアドレス」）から、8 桁の確認コード入力を案内する固定の日本語文字列に差し替え。表示は `white-space: pre-line` を当てて改行させる。`onSubmit()` に 8 桁数字（`/^\d{8}$/`）のバリデーションを追加し、不正な入力はサーバへ送らずローカルで `onDeleteAnswer({ Result: -2 })` として打ち切る。PACKETVER > 20100803 で使う既存のパケット経路（入力値の `substring(2)` を 6 バイトの `YYMMDD` として送信）自体は変更していない。

**依存関係**: `InputBox.js` の `'birthdate'` モード（表示文言・入力属性）。

---

## 7. `src/UI/Components/CharSelect/CharSelectCommon.js`

**目的**: サーバから削除結果 `result = 5`（確認コード不一致。`login.birthdate` との照合失敗）が返ったときのメッセージを差し替える。

**要点**: 2 箇所（既存キャラ一覧側・削除確定後側）で、上流の `DB.getMessage(1822)` を使わず固定文字列「削除確認コードが一致しません。」を表示するよう変更。`msgstringtable.csv` 側で ID 1822 が本来と無関係な文言（`LIMITED`）に上書きされているため、そのまま使うと利用者に誤解を与えることへの対処。

**依存関係**: サーバが返す削除結果コード `5` の意味（`login.birthdate` 不一致）。サーバ側の照合仕様は `server/docs/SPEC.md`（統合予定パス）§7.5 参照。

---

## 8. `src/UI/Components/InputBox/InputBox.js`

**目的**: `CharEngine.js` が呼ぶ `'birthdate'` 入力モードの見た目とバリデーション誘導を、8 桁確認コード方式に合わせる。

**要点**: 表示処理の共通部分に、フォントサイズ・行間のリセットと、`placeholder` / `maxlength` / `autocomplete` / `spellcheck` のリセットを追加（モードを切り替えたときに前のモードの見た目が残らないようにするため）。`'birthdate'` ケースでは案内文言を「削除確認コードを入力してください。」に変更してフォントサイズ 11px・行間 13px を指定し、入力欄には `maxLength=8`、`placeholder='8桁の数字'`、`autocomplete='off'`、`spellcheck=false` を設定する。

**依存関係**: `CharEngine.js` の削除確認フロー。
