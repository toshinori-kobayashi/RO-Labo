#!/usr/bin/env bash
#
# 外部からのポート到達性を確認し、続けて EC2 上の status.sh を実行する（ローカル Mac 用）
#
# 期待値:
#   6900 (login) / 6121 (char) / 5121 (map)  -> open
#   22 (ssh) / 3306 (MariaDB)                -> closed
#
# 使い方:
#   verify.sh                 terraform output の public_ip を対象にする
#   verify.sh --ip 1.2.3.4    IP を直接指定
#   verify.sh --ports-only    リモートの status.sh を実行しない
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,14p' "$0"; exit 0; fi

ip=""
ports_only=0
while [ $# -gt 0 ]; do
	case "$1" in
		--ip) ip="${2:?--ip には IP アドレスが必要です}"; shift 2 ;;
		--ports-only) ports_only=1; shift ;;
		*) die "不明な引数: $1" ;;
	esac
done

require_tools nc
[ -n "$ip" ] || ip="$(public_ip)"

echo "対象: $ip"
echo
printf '%-6s  %-14s  %-8s  %-8s  %s\n' "PORT" "SERVICE" "EXPECT" "ACTUAL" "RESULT"
printf '%-6s  %-14s  %-8s  %-8s  %s\n' "------" "--------------" "--------" "--------" "------"

failed=0
check() {
	local port="$1" service="$2" expect="$3" actual result
	if nc -z -w 5 "$ip" "$port" >/dev/null 2>&1; then
		actual="open"
	else
		actual="closed"
	fi
	if [ "$actual" = "$expect" ]; then
		result="OK"
	else
		result="NG"
		failed=$((failed + 1))
	fi
	printf '%-6s  %-14s  %-8s  %-8s  %s\n' "$port" "$service" "$expect" "$actual" "$result"
}

check 6900 "login-server" open
check 6121 "char-server"  open
check 5121 "map-server"   open
check 22   "ssh"          closed
check 3306 "mariadb"      closed

echo
if [ "$failed" -ne 0 ]; then
	echo "ポート到達性: NG が ${failed} 件あります" >&2
else
	echo "ポート到達性: すべて期待どおり"
fi

if [ "$ports_only" -eq 0 ]; then
	echo
	echo "==================== リモート status ===================="
	ssm_run "/srv/ro-server/app/scripts/status.sh" "ro-server verify" || failed=$((failed + 1))
fi

exit $(( failed == 0 ? 0 : 1 ))
