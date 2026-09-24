#!/usr/bin/env bash
#
# MariaDB のダンプを /srv/ro-server/backups に取る（EC2 上・root 実行）
# systemd ro-server-backup.timer から毎日 04:00 JST に呼ばれる。
#
# 使い方: backup-db.sh [--help]
#
# 認証情報はホスト側の argv に出さないため、コンテナ内の環境変数
# （MARIADB_ROOT_PASSWORD / MARIADB_DATABASE）をコンテナ内のシェルで展開している。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"
BACKUP_DIR="${BACKUP_DIR:-/srv/ro-server/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	sed -n '2,10p' "$0"
	exit 0
fi

cd "$APP_DIR"
mkdir -p "$BACKUP_DIR"

ts="$(date +%Y%m%d-%H%M%S)"
out="$BACKUP_DIR/ragnarok-${ts}.sql.gz"
tmp="${out}.part"

umask 077
# ダンプ / リストアは utf8mb4 で行う。テーブルは utf8mb4、rAthena 本体の接続だけが cp932。
# ここで指定しないとクライアント既定の文字コードで変換されて日本語が壊れる。
echo "backup-db.sh: dump -> ${out}"
if ! docker compose exec -T mariadb sh -c '
		MYSQL_PWD="$MARIADB_ROOT_PASSWORD" exec mariadb-dump \
			--default-character-set=utf8mb4 \
			--single-transaction --quick --routines --events \
			-u root "$MARIADB_DATABASE"
	' | gzip -c > "$tmp"; then
	rm -f "$tmp"
	echo "backup-db.sh: ダンプに失敗しました" >&2
	exit 1
fi

# gzip は空入力でも 20 バイト程度のファイルを作るので、展開後の中身で健全性を見る
raw_bytes="$(gzip -dc "$tmp" | wc -c | tr -d ' ')"
if [ "${raw_bytes:-0}" -lt 1024 ] || ! gzip -dc "$tmp" | grep -q 'CREATE TABLE'; then
	rm -f "$tmp"
	echo "backup-db.sh: ダンプが不完全です（展開後 ${raw_bytes:-0} バイト / CREATE TABLE なし）" >&2
	exit 1
fi

mv "$tmp" "$out"
echo "backup-db.sh: 完了 $(du -h "$out" | cut -f1) ${out}"

echo "backup-db.sh: ${RETENTION_DAYS} 日より古いバックアップを削除します"
find "$BACKUP_DIR" -maxdepth 1 -type f -name 'ragnarok-*.sql.gz' -mtime "+${RETENTION_DAYS}" -print -delete
