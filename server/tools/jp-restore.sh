#!/usr/bin/env bash
#
# NPC 日本語化作業のバックアップからの復元
#
# 指定したバックアップディレクトリの overlay-utf8/ で
# app/rathena/overlay-utf8/ を丸ごと置き換える。
# 実行前に現状を backups/jp-translation/pre-restore-<ts>/ へ退避する。
#
# 使い方:
#   tools/jp-restore.sh --dry-run <backup-dir>   # 差分ファイル一覧だけ表示
#   tools/jp-restore.sh <backup-dir>             # 復元する
#
#   <backup-dir> は backups/jp-translation/<label>-<ts>（相対でも絶対でも可）
#
# 復元後は以下を実行して確認すること:
#   scripts/check-overlay.sh
#   scripts/check-jp-structure.sh
#   tools/gen-jp-conf.py --check
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

dry_run=0
backup_dir=""

while [ $# -gt 0 ]; do
	case "$1" in
		--dry-run) dry_run=1; shift ;;
		-h|--help) sed -n '2,19p' "$0"; exit 0 ;;
		-*) echo "jp-restore.sh: 不明な引数: $1" >&2; exit 2 ;;
		*)
			if [ -n "$backup_dir" ]; then
				echo "jp-restore.sh: バックアップディレクトリは 1 つだけ指定してください" >&2
				exit 2
			fi
			backup_dir="$1"; shift ;;
	esac
done

if [ -z "$backup_dir" ]; then
	sed -n '2,19p' "$0"
	exit 2
fi

# 相対パスはリポジトリルート基準でも解決する
if [ ! -d "$backup_dir" ] && [ -d "$repo_root/$backup_dir" ]; then
	backup_dir="$repo_root/$backup_dir"
fi
backup_dir="$(cd "$backup_dir" 2>/dev/null && pwd || true)"

if [ -z "$backup_dir" ] || [ ! -d "$backup_dir" ]; then
	echo "jp-restore.sh: バックアップディレクトリがありません" >&2
	exit 1
fi

src="$backup_dir/overlay-utf8"
dst="$repo_root/app/rathena/overlay-utf8"

if [ ! -d "$src" ]; then
	echo "jp-restore.sh: overlay-utf8/ がありません: $src" >&2
	echo "  （tools/jp-backup.sh で作ったディレクトリを指定してください）" >&2
	exit 1
fi

echo "バックアップ : ${backup_dir#"$repo_root"/}"
echo "復元先       : ${dst#"$repo_root"/}"
echo

# ---- 差分 -----------------------------------------------------------------
diff_out="$(diff -rq "$src" "$dst" 2>/dev/null || true)"

if [ -z "$diff_out" ]; then
	echo "差分なし（現状はバックアップと同じ内容です）"
	[ "$dry_run" -eq 1 ] && exit 0
	echo "復元する必要はありません。"
	exit 0
fi

n_change=0
n_only_backup=0
n_only_current=0

echo "差分ファイル:"
while IFS= read -r line; do
	case "$line" in
		"Files "*" differ")
			f="${line#Files }"
			f="${f%% and *}"
			printf '  [変更] %s\n' "${f#"$src"/}"
			n_change=$((n_change + 1)) ;;
		"Only in $src"*)
			d="${line#Only in }"
			f="${d%%: *}/${d##*: }"
			printf '  [復元で追加される] %s\n' "${f#"$src"/}"
			n_only_backup=$((n_only_backup + 1)) ;;
		"Only in $dst"*)
			d="${line#Only in }"
			f="${d%%: *}/${d##*: }"
			printf '  [復元で消える] %s\n' "${f#"$dst"/}"
			n_only_current=$((n_only_current + 1)) ;;
		*)
			printf '  %s\n' "$line" ;;
	esac
done <<EOF
$diff_out
EOF

echo
echo "変更 ${n_change} / 復元で追加 ${n_only_backup} / 復元で消える ${n_only_current}"

if [ "$dry_run" -eq 1 ]; then
	echo
	echo "--dry-run のため何も変更していません。"
	exit 0
fi

# ---- 現状を退避 -----------------------------------------------------------
echo
echo "現状を退避します（backups/jp-translation/pre-restore-<ts>/）"
"$repo_root/tools/jp-backup.sh" pre-restore

# ---- 復元 -----------------------------------------------------------------
rm -rf "$dst"
cp -R "$src" "$dst"

echo
echo "復元しました: ${dst#"$repo_root"/}"
echo
echo "次の確認を実行してください:"
echo "  scripts/check-overlay.sh"
echo "  scripts/check-jp-structure.sh"
echo "  tools/gen-jp-conf.py --check"
