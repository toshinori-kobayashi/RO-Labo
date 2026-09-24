#!/usr/bin/env bash
#
# EC2 上の status.sh を SSM 経由で実行する（ローカル Mac 用）
#
# 使い方: status.sh [--tail N]
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,6p' "$0"; exit 0; fi

tail_arg=""
if [ "${1:-}" = "--tail" ]; then
	tail_arg="--tail ${2:?--tail には行数が必要です}"
fi

ssm_run "/srv/ro-server/app/scripts/status.sh ${tail_arg}" "ro-server status"
