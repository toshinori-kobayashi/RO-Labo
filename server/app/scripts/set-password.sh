#!/usr/bin/env bash
#
# 既存アカウントのパスワードを変更する（EC2 上・root 実行）
#
# 使い方:
#   set-password.sh <userid>                 対話: 新パスワードを無エコーで 2 回入力（履歴・ログに残らない）
#   RO_PASSWORD='...' set-password.sh <userid>   非対話: 環境変数から取得（SSM 経由で渡すと実行パラメータに残る点に注意）
#
#   パスワードは ^[A-Za-z0-9_@#%+=.-]{4,23}$（login.user_pass は varchar(32)、use_MD5_passwords: no のため平文保存）
#   値は一切表示・記録しない。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -ne 1 ]; then
	sed -n '2,12p' "$0"; [ $# -eq 1 ] && exit 0; exit 1
fi
userid="$1"
if [[ ! "$userid" =~ ^[A-Za-z0-9_]{4,23}$ ]]; then
	echo "set-password.sh: userid が不正です: $userid" >&2; exit 1
fi

password="${RO_PASSWORD:-}"
if [ -z "$password" ]; then
	if [ ! -t 0 ]; then
		echo "set-password.sh: 非対話実行では RO_PASSWORD を指定してください" >&2; exit 1
	fi
	read -r -s -p "新しいパスワード: " password; echo >&2
	read -r -s -p "確認: " password2; echo >&2
	[ "$password" = "$password2" ] || { echo "set-password.sh: 一致しません" >&2; exit 1; }
fi
if [[ ! "$password" =~ ^[A-Za-z0-9_@#%+=.-]{4,23}$ ]]; then
	echo "set-password.sh: パスワードが不正です（^[A-Za-z0-9_@#%+=.-]{4,23}\$）" >&2; exit 1
fi

cd "$APP_DIR"
db_query() {
	docker compose exec -T mariadb sh -c \
		'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb -N -B --default-character-set=utf8mb4 -u"$MARIADB_USER" "$MARIADB_DATABASE"'
}
sql_quote() { printf '%s' "$1" | sed "s/'/''/g"; }

existing="$(printf "SELECT COUNT(*) FROM \`login\` WHERE \`userid\` = '%s';\n" "$(sql_quote "$userid")" | db_query | tr -d '[:space:]')"
if [ "$existing" != "1" ]; then
	echo "set-password.sh: userid '${userid}' が見つかりません" >&2; exit 1
fi
printf "UPDATE \`login\` SET \`user_pass\` = '%s' WHERE \`userid\` = '%s';\n" "$(sql_quote "$password")" "$(sql_quote "$userid")" | db_query
unset password password2
echo "set-password.sh: '${userid}' のパスワードを変更しました（次回ログインから有効）"
