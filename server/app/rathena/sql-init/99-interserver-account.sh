# inter-server 用アカウント（login.account_id = 1）のパスワードを置き換える。
#
# 実行タイミング: MariaDB 公式イメージの初回初期化（データディレクトリが空のとき）のみ。
# 公式イメージの docker-entrypoint.sh は /docker-entrypoint-initdb.d 配下を
#   *.sh  実行ビットあり -> 実行 / 実行ビットなし -> source
# として処理するため、このファイルは意図的に **実行ビット無し(0644)** にしてある。
# source される前提なので set -euo pipefail は書かない（親シェルの設定を壊すため）。
#
# 01-main.sql が INSERT する既定値は userid='s1' / user_pass='p1' で周知の値。
# ここで .env 由来の生成値へ置き換える。

if [ -z "${INTERSERVER_USER:-}" ] || [ -z "${INTERSERVER_PASSWORD:-}" ]; then
	echo "99-interserver-account.sh: INTERSERVER_USER / INTERSERVER_PASSWORD が未設定です" >&2
	exit 1
fi

# init-env.sh が英数字のみを保証しているが、SQL に直接埋めるのでここでも再検証する。
case "${INTERSERVER_USER}" in
	*[!A-Za-z0-9_]* | '')
		echo "99-interserver-account.sh: INTERSERVER_USER に英数字・アンダースコア以外が含まれています" >&2
		exit 1
		;;
esac
case "${INTERSERVER_PASSWORD}" in
	*[!A-Za-z0-9_]* | '')
		echo "99-interserver-account.sh: INTERSERVER_PASSWORD に英数字・アンダースコア以外が含まれています" >&2
		exit 1
		;;
esac

# rAthena の login.userid は varchar(23) / user_pass は varchar(32)
if [ "${#INTERSERVER_USER}" -gt 23 ] || [ "${#INTERSERVER_PASSWORD}" -gt 23 ]; then
	echo "99-interserver-account.sh: inter-server の userid/passwd は 23 文字以内である必要があります" >&2
	exit 1
fi

echo "99-interserver-account.sh: updating inter-server account (login.account_id = 1)"

docker_process_sql --database="$MARIADB_DATABASE" <<-EOSQL
	UPDATE \`login\` SET \`userid\` = '${INTERSERVER_USER}', \`user_pass\` = '${INTERSERVER_PASSWORD}' WHERE \`account_id\` = 1;
EOSQL
