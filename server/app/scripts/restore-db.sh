#!/usr/bin/env bash
#
# バックアップから MariaDB をリストアする（EC2 上・root 実行）
#
# 使い方:
#   restore-db.sh /srv/ro-server/backups/ragnarok-YYYYmmdd-HHMMSS.sql.gz
#   FORCE=1 restore-db.sh <file>   確認プロンプトを省略（非対話実行用）
#
# login / char / map を停止 -> リストア -> 起動 の順で行う。
# 現在の DB の内容は失われる。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"
FORCE="${FORCE:-0}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -ne 1 ]; then
	sed -n '2,12p' "$0"
	[ $# -eq 1 ] && exit 0
	exit 1
fi

file="$1"
if [ ! -f "$file" ]; then
	echo "restore-db.sh: ファイルがありません: $file" >&2
	exit 1
fi
if [ "$(id -u)" -ne 0 ]; then
	echo "restore-db.sh: root で実行してください" >&2
	exit 1
fi

cd "$APP_DIR"

echo "リストア元: $file ($(du -h "$file" | cut -f1))"
echo "現在の DB の内容は失われます。"
if [ "$FORCE" != "1" ]; then
	read -r -p "続行しますか? [yes/NO]: " answer
	if [ "$answer" != "yes" ]; then
		echo "中止しました"
		exit 1
	fi
fi

echo "=== rAthena 3 サービスを停止 ==="
docker compose stop map-server char-server login-server

# ダンプ / リストアは utf8mb4 で行う。テーブルは utf8mb4、rAthena 本体の接続だけが cp932。
# ここで指定しないとクライアント既定の文字コードで変換されて日本語が壊れる。
echo "=== リストア実行 ==="
if ! zcat "$file" | docker compose exec -T mariadb sh -c '
		MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb --default-character-set=utf8mb4 -u root "$MARIADB_DATABASE"
	'; then
	echo "restore-db.sh: リストアに失敗しました。サービスは停止したままです" >&2
	exit 1
fi

echo "=== rAthena 3 サービスを起動 ==="
docker compose up -d

echo "restore-db.sh: 完了"
"$APP_DIR/scripts/status.sh" --tail 200
