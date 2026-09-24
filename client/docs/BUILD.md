# クライアントの再ビルド手順

ソースの正本は `client/roBrowserLegacy-src/src/` です。上流との差分 8 ファイルは [`PATCHES.md`](PATCHES.md) を参照してください。**ビルド成果物の `Online.js` を直接編集しないでください。** 直すときは必ず `src` を直して、ここに書く手順で再生成します。

## 前提

- Windows x64。`roBrowserLegacy-src/package.json` の `engines.node` は `>=22`。
- Node.js 22 portable を `tools/node/`（未追跡。`.gitignore` 対象。当面このまま、Phase 3 で整理）に置く。管理者権限もシステム PATH の変更も不要。
- ビルド前にそのセッションの PATH の先頭へ通す（PowerShell）:

```powershell
$env:PATH = "<repo>\tools\node;" + $env:PATH
```

Windows 作業コピーの例では `<repo>` は `C:\RO-Lab` です。

## 依存導入

`client/roBrowserLegacy-src/` に `package-lock.json` が無く、素の `npm install` は peer 依存の解決で失敗することがあります。`client/roBrowserLegacy-src/` 直下で次の 2 コマンドを順に実行します。

```powershell
cd <repo>\client\roBrowserLegacy-src

# 1) 主要な依存（electron 等ビルドに不要なものは入れない）
npm install --no-save --legacy-peer-deps --ignore-scripts --omit=optional --no-audit --no-fund `
  vite@^8.0.1 @rollup/plugin-alias@^6.0.0 terser@^5.19.4 bson@^7.2.0 `
  granny-ro-js@~1.5.0 lodash-es@^4.18.1 rijndael-js@^2.0.0 ws@^8.18.0

# 2) vite / lightningcss が Windows x64 で使うネイティブバイナリ（--ignore-scripts なし）
npm install --no-save --legacy-peer-deps --no-audit --no-fund `
  @rolldown/binding-win32-x64-msvc@1.2.9 lightningcss-win32-x64-msvc@1.33.0
```

## 既知の落とし穴

- **lock 無し**: バージョンはこのページに書いた組み合わせで動作確認済み。`npm install` を lock 無しでやり直すと別バージョンが解決されることがある。
- **peer 依存**: `--legacy-peer-deps` を外すと解決に失敗することがある。
- **ネイティブバイナリ 2 つ**: `@rolldown/binding-win32-x64-msvc` と `lightningcss-win32-x64-msvc` は Windows x64 専用。1 回目のコマンドで `--ignore-scripts --omit=optional` を付けているのはこの 2 つを含む optional 依存のビルドスクリプトを走らせないためで、2 回目のコマンドで別途明示的に入れている。

## ビルド

```powershell
node ./applications/tools/builder-web.mjs -O
```

出力先は `dist\Web\` 配下で、成果物は次の 3 ファイルです。

| ファイル | コピー先 |
|---|---|
| `Online.js` | `client\robrowser\Online.js` |
| `ThreadEventHandler.js` | `client\robrowser\ThreadEventHandler.js` |
| `PathFindingWorker.js` | `client\robrowser\PathFindingWorker.js` |

**`Config.local.js` はビルド成果物で上書きしない。** `builder-web.mjs` の出力にも含まれない設定ファイルなので、コピー対象から外すだけでよい。

## 反映確認

Chrome は `Online.js`（約 12MB）をキャッシュするため、コピー後は再読み込みが必要です。反映されていない疑いがあれば URL に `?v=` などクエリを付けて強制的にキャッシュを外します（例: `http://127.0.0.1:8000/api.html?app=ONLINE&v=2`）。

コンソールに次のログが出れば、修正後の `src` が反映されています。

- `[LOGIN] Network Encoding:` / `[LOGIN] GRF Encoding:` — 文字コード分離（`LoginEngine.js` の変更、詳細は [`PATCHES.md`](PATCHES.md)）
- `[skill-jp] applied display names:` / `[skill-jp] applied descriptions:` — スキル日本語化（`DBManager.js` の変更、詳細は [`../README.md`](../README.md) と [`PATCHES.md`](PATCHES.md)）

## 退避

`backup/` は `.gitignore` 対象です。ビルド前の `Online.js` 等をここへコピーしておくと、切り戻しが必要になったときに戻せます。
