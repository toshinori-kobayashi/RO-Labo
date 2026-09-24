#!/usr/bin/env bash
#
# rAthena のアカウントを SSM 経由で作成する（ローカル Mac 用）
#
# 使い方:
#   create-account.sh <userid> <M|F> [group_id]
#   RO_PASSWORD='...' create-account.sh <userid> <M|F> [group_id]
#
#   group_id 99 = GM（Admin）。既定は 0。
#   RO_PASSWORD 未指定ならリモート側で英数 12 桁を生成し、その値が出力される。
#
# 注意: RO_PASSWORD を指定した場合、値は SSM の実行コマンド（send-command の
#       Parameters）に残る。気になる場合は未指定で作成し、出力された値を使うこと。
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,15p' "$0"; exit 0; fi
if [ $# -lt 2 ] || [ $# -gt 3 ]; then sed -n '2,15p' "$0" >&2; exit 1; fi

userid="$1"
sex="$2"
group_id="${3:-0}"

remote="/srv/ro-server/app/scripts/create-account.sh $(shq "$userid") $(shq "$sex") $(shq "$group_id")"
if [ -n "${RO_PASSWORD:-}" ]; then
	remote="RO_PASSWORD=$(shq "$RO_PASSWORD") ${remote}"
fi

ssm_run "$remote" "ro-server create-account"
