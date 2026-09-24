#!/usr/bin/env bash
#
# login テーブルのアカウント一覧を SSM 経由で表示する（ローカル Mac 用）
#
# 使い方: list-accounts.sh
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,6p' "$0"; exit 0; fi

ssm_run "/srv/ro-server/app/scripts/list-accounts.sh" "ro-server list-accounts"
