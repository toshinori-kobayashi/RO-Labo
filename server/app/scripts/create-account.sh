#!/usr/bin/env bash
#
# rAthena のアカウントを login テーブルへ作成する（EC2 上・root 実行）
#
# 使い方:
#   create-account.sh <userid> <M|F> [group_id]
#   RO_PASSWORD='...' create-account.sh <userid> <M|F> [group_id]
#
#   userid    : ^[A-Za-z0-9_]{4,23}$（login.userid は varchar(23)）
#   M|F       : 性別
#   group_id  : 既定 0。GM は 99（conf/groups.yml Id 99 = Admin / all_commands / LogCommands）
#
#   RO_PASSWORD が未設定なら英数 12 桁を生成し、標準出力に 1 回だけ表示する。
#   （use_MD5_passwords: no のため login.user_pass には平文で入る）
#
#   RO_BIRTHDATE='YYYY-MM-DD' で生年月日を指定できる。未指定なら 2000-01-01。
#   生年月日はキャラクター削除の確認コード（クライアントで YYYYMMDD を入力、
#   サーバには下 6 桁 YYMMDD が届く）。PACKETVER 20211103 のクライアントは
#   生年月日でしか削除を確定できないため、必ず値を入れる（NULL だと削除不能）。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"

usage() { sed -n '2,16p' "$0"; }

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then usage; exit 0; fi
if [ $# -lt 2 ] || [ $# -gt 3 ]; then usage >&2; exit 1; fi

userid="$1"
sex="$2"
group_id="${3:-0}"

if [[ ! "$userid" =~ ^[A-Za-z0-9_]{4,23}$ ]]; then
	echo "create-account.sh: userid が不正です（^[A-Za-z0-9_]{4,23}\$ に一致する必要があります）: $userid" >&2
	exit 1
fi
case "$sex" in
	M|F) ;;
	*) echo "create-account.sh: 性別は M か F です: $sex" >&2; exit 1 ;;
esac
if [[ ! "$group_id" =~ ^[0-9]{1,2}$ ]]; then
	echo "create-account.sh: group_id は 0〜99 の整数です: $group_id" >&2
	exit 1
fi
birthdate="${RO_BIRTHDATE:-2000-01-01}"
if [[ ! "$birthdate" =~ ^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$ ]]; then
	echo "create-account.sh: RO_BIRTHDATE は YYYY-MM-DD 形式です: $birthdate" >&2
	exit 1
fi

gen_alnum() {
	local want="$1" out=""
	while [ "${#out}" -lt "$want" ]; do
		out="${out}$(openssl rand -base64 48 | LC_ALL=C tr -dc 'A-Za-z0-9')"
	done
	printf '%s' "${out:0:want}"
}

generated=0
password="${RO_PASSWORD:-}"
if [ -z "$password" ]; then
	password="$(gen_alnum 12)"
	generated=1
fi
if [[ ! "$password" =~ ^[A-Za-z0-9_@#%+=.-]{4,23}$ ]]; then
	echo "create-account.sh: パスワードが不正です（^[A-Za-z0-9_@#%+=.-]{4,23}\$ に一致する必要があります）" >&2
	exit 1
fi

# SQL リテラル用のエスケープ（' -> ''）。上の検証を通っていれば実際には何も起きない
sql_quote() { printf '%s' "$1" | sed "s/'/''/g"; }
q_userid="$(sql_quote "$userid")"
q_password="$(sql_quote "$password")"

cd "$APP_DIR"

# SQL は標準入力から渡す（ホスト側 argv にパスワードを出さないため）。
# 認証情報はコンテナ内の環境変数をコンテナ内のシェルで展開する。
# --default-character-set=utf8mb4 はホスト側スクリプトが UTF-8 で SQL を送る / 受け取るため。
# rAthena 本体の接続は cp932（conf/import/inter_conf.txt の *_codepage）、
# テーブルは utf8mb4 なので、ここで utf8mb4 を指定しないと日本語が化ける。
db_query() {
	docker compose exec -T mariadb sh -c \
		'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --default-character-set=utf8mb4 -N -B -u"$MARIADB_USER" "$MARIADB_DATABASE"'
}
db_table() {
	docker compose exec -T mariadb sh -c \
		'MYSQL_PWD="$MARIADB_PASSWORD" exec mariadb --default-character-set=utf8mb4 --table -u"$MARIADB_USER" "$MARIADB_DATABASE"'
}

existing="$(printf "SELECT COUNT(*) FROM \`login\` WHERE \`userid\` = '%s';\n" "$q_userid" | db_query | tr -d '[:space:]')"
if [ "$existing" != "0" ]; then
	echo "create-account.sh: userid '${userid}' は既に存在します（${existing} 件）" >&2
	exit 1
fi

printf "INSERT INTO \`login\` (\`userid\`, \`user_pass\`, \`sex\`, \`email\`, \`group_id\`, \`birthdate\`) VALUES ('%s', '%s', '%s', 'a@a.com', %s, '%s');\n" \
	"$q_userid" "$q_password" "$sex" "$group_id" "$birthdate" | db_query

account_id="$(printf "SELECT \`account_id\` FROM \`login\` WHERE \`userid\` = '%s';\n" "$q_userid" | db_query | tr -d '[:space:]')"
if [ -z "$account_id" ]; then
	echo "create-account.sh: 作成後の account_id を取得できませんでした" >&2
	exit 1
fi

echo
echo "アカウントを作成しました"
echo "  account_id : ${account_id}"
echo "  userid     : ${userid}"
echo "  sex        : ${sex}"
echo "  group_id   : ${group_id}$( [ "$group_id" = "99" ] && echo '  (Admin)' )"
if [ "$generated" -eq 1 ]; then
	echo "  password   : ${password}    <- 自動生成。この表示は 1 回きりです"
else
	echo "  password   : （RO_PASSWORD で指定した値）"
fi
echo "  birthdate  : ${birthdate}    <- キャラクター削除の確認コード（クライアントでは ${birthdate//-/} と入力）"
echo

printf "SELECT \`account_id\`, \`userid\`, \`sex\`, \`group_id\`, \`birthdate\` FROM \`login\` WHERE \`account_id\` = %s;\n" "$account_id" | db_table
