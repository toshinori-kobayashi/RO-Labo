#!/usr/bin/env bash
#
# app/rathena/overlay-utf8/ の事前チェック（ローカル Mac / Linux 用）
#
# Docker ビルド時に落ちる前に、翻訳ファイルが CP932 へ変換できる状態かを手元で確認する。
# 検査項目:
#   (a) UTF-8 BOM が無い
#   (b) iconv -f UTF-8 -t CP932 が成功する
#   (c) 改行が LF（CR を含まない）
# 加えて U+301C（波ダッシュ）が無いことも見る。
#   glibc の iconv は U+301C を 0x8160 へ通してしまい、macOS の iconv は弾くため、
#   環境差でビルド結果が変わらないよう全角チルダ U+FF5E に揃える。
#
# 使い方:
#   scripts/check-overlay.sh            # リポジトリの app/rathena/overlay-utf8 を検査
#   scripts/check-overlay.sh <dir>      # 任意のディレクトリを検査
#
# 失敗があれば終了コード 1。
#
set -uo pipefail

# macOS の iconv は出力先が /dev/null だと "Inappropriate ioctl for device" で失敗することがあるため、
# 変換結果は一時ファイルへ書く（内容は使わない）。
_cp932_tmp="$(mktemp -t check-overlay)"
trap 'rm -f "$_cp932_tmp"' EXIT

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:-$repo_root/app/rathena/overlay-utf8}"

if [ ! -d "$target" ]; then
	echo "check-overlay.sh: ディレクトリがありません: $target" >&2
	exit 1
fi

# --- iconv が使える CP932 系のエンコーディング名を決める -------------------
# macOS (libiconv) と glibc では対応名が違うことがあるので順に試す。
cp932=""
for enc in CP932 WINDOWS-31J SHIFT_JIS; do
	if printf 'A' | iconv -f UTF-8 -t "$enc" >/dev/null 2>&1; then
		cp932="$enc"
		break
	fi
done
if [ -z "$cp932" ]; then
	echo "check-overlay.sh: iconv が CP932 / WINDOWS-31J / SHIFT_JIS のいずれにも対応していません" >&2
	exit 1
fi

echo "対象      : $target"
echo "iconv 変換: UTF-8 -> $cp932"
echo

wavedash="$(printf '\343\200\234')"   # U+301C
bom="$(printf '\357\273\277')"        # U+FEFF

fail=0
total=0
printf '%-4s %8s  %s\n' "結果" "バイト" "ファイル"
printf '%s\n' "--------------------------------------------------------------------------"

# ファイル名に空白があっても壊れないよう NUL 区切りで回す
while IFS= read -r -d '' f; do
	total=$((total + 1))
	rel="${f#"$target"/}"
	size="$(wc -c < "$f" | tr -d ' ')"
	problems=()

	# (a) UTF-8 BOM
	if [ "$(head -c 3 "$f")" = "$bom" ]; then
		problems+=("UTF-8 BOM あり")
	fi

	# (c) 改行が LF（CR が 1 つでもあれば NG）
	if LC_ALL=C grep -q $'\r' "$f"; then
		problems+=("CR を含む（CRLF / CR）")
	fi

	# U+301C
	if LC_ALL=C grep -q "$wavedash" "$f"; then
		problems+=("U+301C 波ダッシュ（U+FF5E 全角チルダを使う）")
	fi

	# (b) CP932 へ変換できるか
	# 失敗したら該当行を特定して出す（macOS の iconv はエラー文言が errno 由来で当てにならない）
	if ! iconv -f UTF-8 -t "$cp932" "$f" > "$_cp932_tmp" 2>/dev/null; then
		bad_lines=""
		n=0
		while IFS= read -r l; do
			n=$((n + 1))
			if ! printf '%s\n' "$l" | iconv -f UTF-8 -t "$cp932" > "$_cp932_tmp" 2>/dev/null; then
				bad_lines="${bad_lines}${bad_lines:+, }${n}"
			fi
		done < "$f"
		if [ -n "$bad_lines" ]; then
			problems+=("CP932 に変換できない文字があります（行: ${bad_lines}）")
		else
			problems+=("CP932 に変換できない文字があります")
		fi
	fi

	if [ "${#problems[@]}" -eq 0 ]; then
		printf '%-4s %8s  %s\n' "OK" "$size" "$rel"
	else
		fail=$((fail + 1))
		printf '%-4s %8s  %s\n' "NG" "$size" "$rel"
		for p in "${problems[@]}"; do
			printf '%-4s %8s    -> %s\n' "" "" "$p"
		done
	fi
done < <(find "$target" -type f -print0 | LC_ALL=C sort -z)

echo
if [ "$total" -eq 0 ]; then
	echo "ファイルが 1 つもありません: $target"
	exit 1
fi

if [ "$fail" -gt 0 ]; then
	echo "NG: ${total} ファイル中 ${fail} ファイルに問題があります"
	exit 1
fi

echo "OK: ${total} ファイルすべて CP932 へ変換できます"
