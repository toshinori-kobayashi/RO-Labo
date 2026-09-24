#!/usr/bin/env bash
#
# NPC 日本語化作業のバックアップ
#
# 翻訳バッチを始める前 / 大きな一括置換の前に実行する。
# backups/jp-translation/<label>-<YYYYmmdd-HHMMSS>/ に以下をコピーする:
#   overlay-utf8/            … app/rathena/overlay-utf8 全体
#   docs/JP_GLOSSARY.md      … あれば
#   tools/                   … 検証・生成ツール一式
#   scripts/check-jp-structure.sh / check-overlay.sh / local-smoke.sh
#   RESTORE.md               … 復元手順
#   MANIFEST-snapshot.tsv    … その時点の MANIFEST.tsv
#   sha256sums.txt           … バックアップ内全ファイルのハッシュ
#
# 使い方:
#   tools/jp-backup.sh <label>
#   例: tools/jp-backup.sh before-batch-2
#
# 復元は tools/jp-restore.sh <backup-dir>。
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ $# -lt 1 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	sed -n '2,20p' "$0"
	exit 0
fi

label="$1"
case "$label" in
	*/*|*" "*)
		echo "jp-backup.sh: label に / や空白は使えません: $label" >&2
		exit 2 ;;
esac

ts="$(date '+%Y%m%d-%H%M%S')"
dest="$repo_root/backups/jp-translation/${label}-${ts}"

overlay="$repo_root/app/rathena/overlay-utf8"
if [ ! -d "$overlay" ]; then
	echo "jp-backup.sh: overlay がありません: $overlay" >&2
	exit 1
fi

mkdir -p "$dest"

echo "バックアップ先: ${dest#"$repo_root"/}"

# --- overlay 全体 ---------------------------------------------------------
cp -R "$overlay" "$dest/overlay-utf8"

# --- 用語集（あれば） -----------------------------------------------------
if [ -f "$repo_root/docs/JP_GLOSSARY.md" ]; then
	mkdir -p "$dest/docs"
	cp "$repo_root/docs/JP_GLOSSARY.md" "$dest/docs/JP_GLOSSARY.md"
fi

# --- ツール類 -------------------------------------------------------------
if [ -d "$repo_root/tools" ]; then
	cp -R "$repo_root/tools" "$dest/tools"
fi
mkdir -p "$dest/scripts"
for s in check-jp-structure.sh check-overlay.sh local-smoke.sh; do
	if [ -f "$repo_root/scripts/$s" ]; then
		cp "$repo_root/scripts/$s" "$dest/scripts/$s"
	fi
done

# --- MANIFEST スナップショット --------------------------------------------
manifest="$overlay/npc/custom/jp/MANIFEST.tsv"
if [ -f "$manifest" ]; then
	cp "$manifest" "$dest/MANIFEST-snapshot.tsv"
else
	echo "# MANIFEST.tsv は存在しませんでした（${ts}）" > "$dest/MANIFEST-snapshot.tsv"
fi

n_files="$(find "$dest/overlay-utf8" -type f | wc -l | tr -d ' ')"
n_jp="$(find "$dest/overlay-utf8/npc/custom/jp" -type f -name '*.txt' 2>/dev/null | wc -l | tr -d ' ')"

# --- 復元手順 -------------------------------------------------------------
rel_dest="backups/jp-translation/${label}-${ts}"
cat > "$dest/RESTORE.md" <<RESTORE_EOF
# 復元手順（${label} / ${ts} 時点）

対象リポジトリ: \`$(basename "$repo_root")\`（このファイルの 3 階層上）

## 中身

| パス | 内容 |
|---|---|
| \`overlay-utf8/\` | \`app/rathena/overlay-utf8\` 全体（${n_files} ファイル。うち翻訳 NPC ${n_jp} ファイル） |
| \`MANIFEST-snapshot.tsv\` | この時点の \`npc/custom/jp/MANIFEST.tsv\` |
| \`tools/\` | 生成・検証ツール一式（gen-jp-conf.py / jp_structure_check.py / jp-backup.sh / jp-restore.sh） |
| \`scripts/\` | check-jp-structure.sh / check-overlay.sh / local-smoke.sh |
| \`docs/JP_GLOSSARY.md\` | 用語集（存在した場合のみ） |
| \`sha256sums.txt\` | 上記すべてのハッシュ |

## 戻しかた（推奨）

\`\`\`bash
# 差分だけ確認
tools/jp-restore.sh --dry-run ${rel_dest}

# 実行（現状は backups/jp-translation/pre-restore-<ts>/ へ退避される）
tools/jp-restore.sh ${rel_dest}
\`\`\`

## 手で戻す場合

\`\`\`bash
rm -rf app/rathena/overlay-utf8
cp -R "${rel_dest}/overlay-utf8" app/rathena/overlay-utf8
\`\`\`

## 戻したあとの確認

\`\`\`bash
scripts/check-overlay.sh          # BOM / LF / CP932
scripts/check-jp-structure.sh     # 上流との構造一致
tools/gen-jp-conf.py --check      # scripts_custom.conf と MANIFEST の整合
scripts/local-smoke.sh --expect-npcs 13043
\`\`\`

## 整合性の確認

\`\`\`bash
cd ${rel_dest} && shasum -a 256 -c sha256sums.txt
\`\`\`
RESTORE_EOF

# --- ハッシュ -------------------------------------------------------------
(
	cd "$dest"
	find . -type f ! -name sha256sums.txt -print0 \
		| LC_ALL=C sort -z \
		| xargs -0 shasum -a 256 > sha256sums.txt
)

echo "  overlay-utf8   : ${n_files} ファイル（翻訳 NPC ${n_jp} ファイル）"
echo "  RESTORE.md / MANIFEST-snapshot.tsv / sha256sums.txt を作成しました"
echo
echo "復元: tools/jp-restore.sh --dry-run ${rel_dest}"
