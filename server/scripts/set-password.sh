#!/usr/bin/env bash
#
# 既存アカウントのパスワードを SSM 経由で変更する（ローカル Mac 用）
#
# 使い方:
#   RO_PASSWORD='...' scripts/set-password.sh <userid>
#
# 注意: RO_PASSWORD の値は SSM Run Command の実行パラメータに残る（SSM コンソール等から参照可能）。
#       残したくない場合は scripts/ssm-shell.sh で入り、
#       sudo /srv/ro-server/app/scripts/set-password.sh <userid> を対話実行すること（無エコー入力・履歴に残らない）。
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -ne 1 ]; then sed -n '2,11p' "$0"; [ $# -eq 1 ] && exit 0; exit 1; fi
[ -n "${RO_PASSWORD:-}" ] || die "RO_PASSWORD を指定してください（対話で設定したい場合は ssm-shell.sh を使う）"

ssm_run "RO_PASSWORD=$(shq "$RO_PASSWORD") /srv/ro-server/app/scripts/set-password.sh $(shq "$1")" "ro-server set-password"
