#!/usr/bin/env bash
#
# CloudWatch Logs からコンテナのログを取得する（ローカル Mac 用・EC2 には入らない）
#
# 使い方:
#   logs.sh                        全ストリームを直近 10 分ぶん
#   logs.sh map-server             map-server のみ
#   logs.sh map-server --since 1h  期間を指定
#   logs.sh login-server --follow  追尾
#
#   service: login-server | char-server | map-server | mariadb
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,12p' "$0"; exit 0; fi

service=""
since="10m"
follow=()

while [ $# -gt 0 ]; do
	case "$1" in
		--since) since="${2:?--since には 10m / 1h / 2d などを指定してください}"; shift 2 ;;
		--follow|-f) follow=(--follow); shift ;;
		login-server|char-server|map-server|mariadb) service="$1"; shift ;;
		*) die "不明な引数: $1" ;;
	esac
done

require_tools aws
group="$(log_group)"

args=(logs tail "$group" --since "$since" --format short)
if [ -n "$service" ]; then
	args+=(--log-stream-names "$service")
fi
if [ "${#follow[@]}" -gt 0 ]; then
	args+=("${follow[@]}")
fi

info "aws logs tail ${group} (${service:-all streams}, since ${since})"
exec aws --profile "$AWS_PROFILE" --region "$REGION" "${args[@]}"
