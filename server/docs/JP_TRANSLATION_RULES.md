# NPC スクリプト翻訳ルール（翻訳担当が必ず守ること）

対象は rAthena の NPC スクリプト（`.txt`）。**構造を一切変えず、プレイヤーに表示される文字列だけを日本語化する。** 用語は `docs/JP_GLOSSARY.md` に従う（新語はまず用語集に追記）。

## 配置

- 上流 `npc/<path>` → 翻訳版 `app/rathena/overlay-utf8/npc/custom/jp/<path>`（上流パスの鏡写し。`npc/pre-re/...` は `pre-re/...` を含めてそのまま）。
- 原本は上流 rAthena（`app/config.env` の `RATHENA_COMMIT`）から読む。`tools/jp_common.py` が `~/.cache/rathena-<commit>/` に自動取得する（ローカル checkout があれば環境変数 `RATHENA_UPSTREAM_ROOT` で指定）。**原本を編集しない。**
- 出力は UTF-8（BOM なし）・LF・原本と同じタブ/スペース。

## 変更してよいもの（文字列リテラルの中身のみ）

`mes "..."`, `select("a:b:c")`, `prompt(...)`, `menu "a",L_a,"b",L_b`, `dispbottom`, `message`, `announce`/`mapannounce` の**メッセージ側**, `npctalk`, `unittalk`, `showscript`, `viewpoint` のラベル文字列（あれば）、話者タグ `mes "[Name]"`、`callfunc` の**2 番目以降**の引数が表示用文字列である場合。

## 変更してはいけないもの

- ヘッダ行（`map,x,y,dir<TAB>script<TAB>Name::Unique<TAB>sprite,{`）の座標・種別・sprite・`duplicate(Source)` のソース名。表示名は **`::ユニーク名` がある場合のみ**日本語化可。`::` が無いヘッダ、`function<TAB>script<TAB>F_Name` は変更しない。
- 関数名・ラベル名（`L_xxx:`, `OnInit:`, `OnTimer1000:`）・変数名（`.@x`, `$@y$`, `job_sword_q` 等）・定数・数値・`;` `{}` `()` `,`・演算子・タブ・改行構造・行数。
- `//` コメント（原文のまま残す。行末に新しいコメントも追加しない）。
- `^RRGGBB` 色コードとその位置関係、`%s` `%d` `%.*s` などの書式指定子の個数・順序、`"..." + 変数 + "..."` の連結構造。
- **識別子として使われる文字列**: `warp "prontera",x,y` / `savepoint` / `areawarp` のマップ名、`callfunc "F_..."` の関数名、`doevent`/`donpcevent` の `"Name::OnEvent"`、`enablenpc`/`disablenpc`/`hideonnpc`/`hideoffnpc` の NPC 名、`getvariableofnpc`、`monster "map",...` のマップ名、`setmapflag` 等。
- `if (.@x$ == "Save")` のような**比較に使われる文字列**: 訳す場合は同一ファイル内の「代入側（`set`/`setarray` の文字列）」と「比較側」を**完全に同じ日本語**にする。外部ファイルから来る値と比較している場合は訳さない。迷ったら英語のまま残し、報告に理由を書く（ファイル内に `JP-TODO` コメントは入れない）。

## 文字列の中身のルール

- `select`/`prompt`/`menu` の項目は `:` の**個数と順序を維持**。項目内に `:` を使わない。
- 日本語文字の直後に `\"` や `\\` を置かない（rAthena のパーサ仕様）。引用は「」。
- 使用可能: JIS X 0208 + ASCII。禁止: U+301C「〜」（→ U+FF5E「～」）、U+2212「−」（→「－」）、絵文字、半角カナ、機種依存文字。
- `mes` 1 行は全角 22 文字目安。行の追加・削除はしない（原本の行数の中で割り付け直す）。
- 原本に非 ASCII バイト（韓国語ファイル名など。例 `npc/jobs/2-1/priest.txt` の `cutin "...bmp"`）が含まれる場合、そのバイト列は UTF-8 に変換せず `\xB9\xCC` 形式の 16 進エスケープで**同じバイト列**を書く（`xxd` で原本のバイトを確認する）。rAthena は文字列読み込み時に `\x` を 1 バイトへ戻すので、クライアントには原本と同一のバイトが届く。ヘッダ（NPC 名）に非 ASCII バイトがある場合は翻訳せず、担当へ相談する。
- **添字式 `var[ ... ]` の中に置く文字列**（例 `.@Items[select("…")]`、`.@a[callfunc("F_X","…")]`）には、CP932 で 2 バイト目が `[`(0x5B) / `]`(0x5D) になる文字を入れない: 「ー」「ゼ」「ゾ」「‐」および 閏 骸 擬 啓 梗 纂 充 深 措 端 甜 納 票 房 夕 麓 / 云 馨 犠 珪 江 讃 従 疹 曽 綻 転 脳 評 望 余 肋 など計 104 字（`tools/jp_structure_check.py` の 1c が列挙する）。rAthena の `parse_variable()` が添字の対応 `]` を文字列も 2 バイト文字も見ない生バイト走査で探すため、数が合わないとファイル末尾を越えて読み進み map-server が SIGSEGV で落ちる（起動時、再現は不定）。言い換えで避けられないアイテム名などはその箇所だけ英語表記にする（`getitemname()` が英語なので整合する）。通常の `mes` の中では問題ない。
- 通貨は文字列内でも `Zeny` 表記（`zeny`・`ゼニー` は使わない。変数名 `.@zeny_req` 等のコードは対象外）。
- 文体・用語は `docs/JP_GLOSSARY.md`。同一 NPC の話者タグは統一。原文の意味を保った独自訳とし、jRO 公式文の再現・転載はしない。

## 完了前の自己検証（結果を報告に貼る）

```sh
ORIG=<原本パス>; NEW=<翻訳版パス>
# 1) 文字列を潰した構造 diff（ヘッダの表示名以外に差分が出たら修正）
diff <(perl -pe 's/"(?:[^"\\]|\\.)*"/""/g' "$ORIG") <(perl -pe 's/"(?:[^"\\]|\\.)*"/""/g' "$NEW")
# 2) 行数・mes 行数一致
wc -l "$ORIG" "$NEW"; grep -cE '^\s*mes\s+"' "$ORIG" "$NEW"
# 3) select/prompt の ':' 個数が行ごとに一致
diff <(grep -nE 'select\(|prompt\(' "$ORIG" | awk -F: '{print gsub(/:/,":")}') <(grep -nE 'select\(|prompt\(' "$NEW" | awk -F: '{print gsub(/:/,":")}')
# 4) CP932 変換可・BOM なし・CRLF なし
iconv -f UTF-8 -t CP932 "$NEW" > "$(mktemp)" && echo CP932-OK; head -c 3 "$NEW" | od -An -tx1; grep -c $'\r' "$NEW"   # macOS の iconv は > /dev/null だと誤検知するので一時ファイルへ
# 4b) 通貨表記（何も出なければ OK）
grep -nE '"[^"]*(zeny|ゼニー)' "$NEW"
# 5) 構造検証ツールがあれば必ず実行して PASS にする
[ -x scripts/check-jp-structure.sh ] && scripts/check-jp-structure.sh --file "$NEW" --upstream "<上流パス npc/...>"
```

先頭コメントの追加は行わない（行数を原本と一致させるため。以前のファイルで追加した 1 行は例外として残す）。

## NPC 頭上表示名（第 2 フェーズ、2026-09-24 追加）

rAthena は `表示名::ユニーク名` のうち **ユニーク名（exname）だけ**で NPC を参照する（`src/map/npc.cpp` `npc_parsename` / `npcname_db`）。`doevent` / `donpcevent` / `enablenpc` / `disablenpc` / `getvariableofnpc` / `getnpcid` / `duplicate()` / `"名前::OnEvent"` はすべて exname 解決。したがって頭上名は次の形で日本語化する。

- 上流 `Kafra Employee#prt` → 翻訳版 `カプラ職員#prt::Kafra Employee#prt`（表示は「カプラ職員」、`#prt` は `strnpcinfo(2)` 用に引き継ぐ、exname は旧フル名のまま）
- 上流 `Guide#gef::GefGuide` → 翻訳版 `案内係#gef::GefGuide`（ユニーク名は不変）
- 日本語部分に `::` `#` タブ・制御文字を入れない。表示名（`#suffix` 込み）は CP932 で 50 バイト以内（`NPC_NAME_LENGTH`）。
- 本文や他ファイルが `strnpcinfo(0)` / `strnpcinfo(1)`（可視名）を **比較やキー**に使う NPC は英語のまま（例 `merchants/coin_exchange.txt` の "Merchant of Manuk"）。`strnpcinfo(2)/(3)/(4)` は上記の形なら影響なし。
- 不可視 NPC（浮動 `-`、`function`、sprite -1、`#` で始まる名前）、warp、shop は対象外。
- duplicate の表示名は参照元と同じ日本語にする（`#suffix` は各自のものを引き継ぐ）。
- 表示名は話者タグ（`mes "[…]"`）と一致させる。対応表 `docs/jp-npc-names.tsv` が Source of Truth で、`tools/jp_npc_names.py apply` で機械的に書き換える（手編集しない）。
