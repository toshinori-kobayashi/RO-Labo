#!/usr/bin/env bash
#
# 既存アカウントの生年月日（キャラクター削除の確認コード）を設定する（EC2 上・root 実行）
#
# 使い方:
#   set-birthdate.sh <userid> [YYYY-MM-DD]     省略時は 2000-01-01
#   set-birthdate.sh --all-missing [YYYY-MM-DD] 生年月日が NULL の全アカウントにまとめて設定（inter-server 用の account_id 1 は除く）
#
#   PACKETVER 20211103 のクライアントは 0x0829（生年月日 YYMMDD）でしか削除を確定できず、
#   login.birthdate が NULL のアカウントはキャラクターを削除できない。
#   クライアントには YYYYMMDD（例 20000101）を入力する。パスワード等の秘密情報は扱わない。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"

usage() { sed -n '2,12p' "$0"; }
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -lt 1 ] || [ $# -gt 2 ]; then
	usage; [ $# -ge 1 ] && [ $# -le 2 ] && exit 0; exit 1
fi

target="$1"
birthdate="${2:-2000-01-01}"
if [[ ! "$birthdate" =~ ^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$ ]]; then
	echo "set-birthdate.sh: 生年月日は YYYY-MM-DD 形式です: $birthdate" >&2; exit 1
fi

cd "$APP_DIR"
db_query() {
	docker compose exec -T mariadb sh -c \
		'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb -N -B --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'
}
db_table() {
	docker compose exec -T mariadb sh -c \
		'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --table --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'
}
sql_quote() { printf '%s' "$1" | sed "s/'/''/g"; }

if [ "$target" = "--all-missing" ]; then
	printf "UPDATE \`login\` SET \`birthdate\` = '%s' WHERE \`birthdate\` IS NULL AND \`account_id\` <> 1;\n" "$birthdate" | db_query
	echo "set-birthdate.sh: 生年月日が未設定だったアカウントに ${birthdate} を設定しました"
	printf "SELECT \`account_id\`, \`userid\`, \`group_id\`, \`birthdate\` FROM \`login\` WHERE \`account_id\` <> 1 ORDER BY \`account_id\`;\n" | db_table
	exit 0
fi

userid="$target"
if [[ ! "$userid" =~ ^[A-Za-z0-9_]{4,23}$ ]]; then
	echo "set-birthdate.sh: userid が不正です: $userid" >&2; exit 1
fi
existing="$(printf "SELECT COUNT(*) FROM \`login\` WHERE \`userid\` = '%s';\n" "$(sql_quote "$userid")" | db_query | tr -d '[:space:]')"
if [ "$existing" != "1" ]; then
	echo "set-birthdate.sh: userid '${userid}' が見つかりません" >&2; exit 1
fi
printf "UPDATE \`login\` SET \`birthdate\` = '%s' WHERE \`userid\` = '%s';\n" "$birthdate" "$(sql_quote "$userid")" | db_query
echo "set-birthdate.sh: '${userid}' の生年月日を ${birthdate} にしました（削除時はクライアントで ${birthdate//-/} と入力。次回 char-server ログインから有効）"
printf "SELECT \`account_id\`, \`userid\`, \`group_id\`, \`birthdate\` FROM \`login\` WHERE \`userid\` = '%s';\n" "$(sql_quote "$userid")" | db_table
