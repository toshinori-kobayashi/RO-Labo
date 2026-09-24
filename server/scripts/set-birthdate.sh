#!/usr/bin/env bash
#
# 既存アカウントの生年月日（キャラクター削除の確認コード）を SSM 経由で設定する（ローカル Mac 用）
#
# 使い方:
#   scripts/set-birthdate.sh <userid> [YYYY-MM-DD]      省略時は 2000-01-01
#   scripts/set-birthdate.sh --all-missing [YYYY-MM-DD]  生年月日が NULL の全アカウントに設定
#
#   クライアントの削除確認ダイアログには YYYYMMDD（例 20000101）を入力する。
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -lt 1 ] || [ $# -gt 2 ]; then sed -n '2,10p' "$0"; [ $# -ge 1 ] && [ $# -le 2 ] && exit 0; exit 1; fi

remote="/srv/ro-server/app/scripts/set-birthdate.sh $(shq "$1")"
[ $# -eq 2 ] && remote="${remote} $(shq "$2")"
ssm_run "$remote" "ro-server set-birthdate"
