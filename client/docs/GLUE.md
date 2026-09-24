# ro-glue 仕様

`ro-glue` は `tools/ro-glue/server.mjs`（Phase 2 で `client/ro-glue/` へ移動予定）の 1 ファイル・1 プロセスで動く自作 Node（ESM、依存は `ws` のみ、`package.json` は GPL-3.0-or-later）です。本書はこのファイルを読んで書いています。起動コマンドの例は [`../README.md`](../README.md) を参照してください。

## 責務

1. **静的配信** — ビルド済み roBrowserLegacy Web ビルド（`Config.local.js` を含む）を配信する。
2. **資産配信 `/client/<path>`** — `data.grf`（GRF 0x200 / 0x300）と loose フォルダから、クライアントが要求したファイルを読み取り専用で返す。
3. **WebSocket → TCP 中継** — ブラウザの WebSocket を許可先 TCP へつなぐ。

**ro-glue はパケットの中身にも文字コードにも意味的な変換を一切加えません。** 中継するバイト列はサーバ・クライアント間でそのまま透過します。資産配信のパス解決で行う文字コード変換（後述）は、ファイル名の照合のためだけのものであり、ファイルの中身やゲーム通信のペイロードには手を加えません。

## CLI オプションと既定値

```
node server.mjs --port 8000 --static <dir> [--grf <file.grf> ...] [--loose <dir> ...]
                [--allow <ip:port>[,<ip:port>...] ...] [--decrypt <path>] [--verbose] [--dump-rx <path>]
```

| オプション | 既定値 | 備考 |
|---|---|---|
| `--port <n>` | `8000` | |
| `--static <dir>` | なし（**必須**） | 未指定なら `--static <dir> is required` を出して終了（exit code 2） |
| `--grf <file>` | `[]`（複数指定可） | 指定順が資産解決の優先順になる |
| `--loose <dir>` | `[]`（複数指定可） | 指定順が資産解決の優先順になる |
| `--allow <ip:port,...>` | `[]`（複数回指定するとカンマ区切りをまとめて集合に追加） | **空のまま起動すると WS 中継の宛先制限が効かず、どの宛先へも中継してしまう**（`allowSet.size` が 0 だと許可リスト判定自体をスキップするため）。実運用では必ず指定する |
| `--decrypt <path>` | `path.resolve('..', 'roBrowserLegacy-src', 'src', 'Loaders', 'GameFileDecrypt.js')`（プロセスの **CWD 起点**） | `tools/ro-glue/` で起動する前提の相対解決。別ディレクトリから起動する場合は明示指定が必要 |
| `--verbose` | `false` | 資産 404 のたびにログを出す（既定では初回のみ） |
| `--dump-rx <path>` | 未指定（ダンプしない） | サーバ→クライアント方向のバイト列のみを追記ダンプ。クライアント→サーバ（パスワードを含みうる）は書かない |

未知の引数は黙って無視されます（エラーにならない）。

## 静的配信

`opt.static` 配下をそのまま返します。`GET /` は `/api.html` に読み替えます。パスは `safeJoin()` で正規化し、`opt.static` の外へ出るパスは拒否します。

## `/client/` の解決順（loose → GRF）

`GET /client/<path>` は次の順で探します。最初に見つかったもので確定です。

1. **loose フォルダ**（`--loose` を指定した順）— 各候補パスを `fs.existsSync` + `isFile` で確認
2. **GRF**（`--grf` を指定した順）— `Grf#find()` でエントリを探し、見つかれば復号・展開して返す
3. どちらにも無ければ 404（`missLog` に記録。`--verbose` か初回のみコンソールに出す）

その他のエンドポイント:

| エンドポイント | 役割 |
|---|---|
| `POST /client/` body `filter=<regex>` | GRF 内のファイル名を正規表現検索（結果は latin1 名の改行区切りテキスト） |
| `POST /client/batch` body JSON `{"files":[...]}` | 複数ファイルを一括取得（各ファイルを base64 にした JSON マップ） |
| `GET /__status` | `{stats:{hits,misses}, grfs:[{path,version,files}], misses:[...]}`（misses は先頭 200 件） |

## GRF 実装要点

- GRF 0x200（旧形式）と 0x300（"Event Horizon"、64bit オフセット）の両方を読む。シグネチャは先頭 15 バイトの `Master of Magic` / `Event Horizon`。
- ファイルテーブルは zlib 圧縮。展開後、エントリごとに `name\0` + `packSize/lengthAligned/realSize`（u32×3）+ `type`（u8）+ `offset`（0x300 は u64、0x200 は u32）を読む。`type & 0x01`（TYPE_FILE）以外のエントリ（フォルダ等）は読み飛ばす。
- 暗号化フラグは標準 Gravity DES の 2 種類のみ扱う: `0x02`（TYPE_ENCRYPT_MIXED、ヘッダ+本体）と `0x04`（TYPE_ENCRYPT_HEADER、ヘッダのみ）。`.gnd` `.gat` `.act` `.str` はヘッダのみ復号（`SKIP_EXTENSIONS`）、それ以外は全体を復号。復号後、先頭バイトが zlib ヘッダ `0x78` であることを確認してから `zlib.inflateSync` する。復号処理自体は roBrowserLegacy 同梱の `GameFileDecrypt.js`（`--decrypt` で指定、GPL）を import して使う。
- GRF 内のファイル名は EUC-KR バイト列（kRO 形式パス、例 `유저인터페이스`）。ブラウザ側（roBrowser Worker）は同じバイトを windows-1252 としてデコードしてから要求してくることがあるため、ro-glue は要求パスを次の 2 通りで照合する:
  - 受け取った文字列をそのまま windows-1252/latin1 の生バイト列に戻した「latin1 キー」（`toRawBytes` / `toLatin1Key`。0x80–0x9F の CP1252 特殊文字は逆引きテーブルで戻す）
  - 上記の生バイト列を EUC-KR として再解釈した「EUC-KR キー」
  - GRF 側もロード時に両方のキー（`byLatin1` / `byEucKr`）でエントリを索引しておき、`find()` はまず latin1 キー、無ければ EUC-KR キーを見る。
- HTTP リクエストパスの URL デコードで不正な UTF-8 パーセントエスケープが出た場合（EUC-KR の生バイトをそのままパーセントエンコードしてきた場合など）は、`decodeURIComponent` の例外を捕まえて、パーセント列をそのまま latin1 の 1 バイト＝1 文字として解釈するフォールバックを行う。

## WS → TCP 中継

- 接続先は URL パス `/<ip>:<port>`（例 `ws://127.0.0.1:8000/<ip>:<port>`。実際の宛先値は [`../README.md`](../README.md) の Config.local.js 抜粋・起動コマンド例を参照）。`^\/([^/:]+):(\d+)\/?$` にマッチしない、または `--allow` の集合に無い宛先は `403 Forbidden` を返して即座にソケットを破棄する。
- 1 つの WebSocket 接続につき `net.connect()` で TCP ソケットを 1 本だけ張る（1 WS = 1 TCP、コネクションプーリングなし）。
- 中継はどちらの方向も生バイトのまま: TCP `data` → `ws.send(d)`、WS `message` → `tcp.write(b)`。**変換・加工は一切しない。**
- 片方が閉じたら他方も閉じる（`tcp.close` → `ws.close()`、`ws.close` → `tcp.destroy()`）。close 時に受信/送信バイト数をログに出す。
- `--dump-rx <path>` はサーバ→クライアント方向（`tcp.on('data')`）のみを対象に、タイムスタンプ・宛先・長さ・16 進ダンプ・latin1 プレビューをファイルへ追記する。クライアント→サーバ方向（ログイン時のパスワード等を含みうる）は一切ダンプしない。

## セキュリティ上の前提

- `server.listen(opt.port, '127.0.0.1', ...)` で **127.0.0.1 のみ** listen する。外部ネットワークからは到達できない。
- GRF・loose への操作は読み取りのみ（`fs.readFileSync` / オフセット指定の読み取り）。書き込みは一切行わない。
- HTTP レスポンスには `Access-Control-Allow-Origin: '*'` を付けている。127.0.0.1 バインドのため実害は限定的だが、同一マシン上の他プロセスからは資産取得やステータス参照ができる前提で扱うこと。
- WS 中継は `--allow` を指定して初めて宛先が絞られる。**`--allow` を付け忘れると任意の宛先へ中継してしまう**ので、起動コマンドには必ず含めること（例は [`../README.md`](../README.md)）。
- 外部（`https://grf.robrowser.com/` 等）へ資産を取りに行く経路はここには無い。クライアント側で `remoteClient` をこの glue に固定する設定と合わせて、資産が外部へ出ない構成になっている。
