#!/usr/bin/env bash
#
# NPC 翻訳ファイルの構造検証（tools/jp_structure_check.py の薄いラッパ）
#
# 翻訳版が上流 rAthena（app/config.env の RATHENA_COMMIT）に対して
# 「文字列リテラルの中身以外は同一」であることを機械判定する。
#
# 使い方:
#   scripts/check-jp-structure.sh                       # MANIFEST.tsv 全件
#   scripts/check-jp-structure.sh --report /tmp/jp.txt  # 結果をファイルにも保存
#   scripts/check-jp-structure.sh \
#       --file app/rathena/overlay-utf8/npc/custom/jp/cities/prontera.txt \
#       --upstream npc/cities/prontera.txt              # 単体検証
#
# 引数はそのまま tools/jp_structure_check.py に渡る（--upstream-root / --commit /
# --strict-external-refs など）。
#
# エンコーディング（BOM / LF / CP932）だけを見たいときは scripts/check-overlay.sh。
# 両方 PASS を apply の前提にすること。
#
# FAIL があれば終了コード 1。
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	sed -n '2,21p' "$0"
	exit 0
fi

python3="$(command -v python3 || true)"
if [ -z "$python3" ]; then
	echo "check-jp-structure.sh: python3 が見つかりません" >&2
	exit 2
fi

exec "$python3" "$repo_root/tools/jp_structure_check.py" "$@"
