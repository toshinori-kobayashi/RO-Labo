#!/usr/bin/env bash
#
# login テーブルのアカウント一覧を表示する（EC2 上・root 実行）
#
# 使い方: list-accounts.sh [--help]
#
# account_id=1 は inter-server 用のシステムアカウント（sex='S'）。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	sed -n '2,8p' "$0"
	exit 0
fi

cd "$APP_DIR"

printf 'SELECT `account_id`, `userid`, `sex`, `group_id`, `logincount`, `lastlogin`, `last_ip` FROM `login` ORDER BY `account_id`;\n' \
	| docker compose exec -T mariadb sh -c \
		'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --default-character-set=utf8mb4 --table -u"$MARIADB_USER" "$MARIADB_DATABASE"'
