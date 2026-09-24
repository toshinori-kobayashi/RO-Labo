#!/usr/bin/env bash
#
# EC2 上のデプロイ本体（root 実行・冪等）
#
# 呼び出し元: Terraform 側の SSM ドキュメントが
#   user-data 完了待ち -> S3 から app.zip 取得 -> 一時展開
#   -> rsync -a --delete --exclude .env で /srv/ro-server/app へ同期
#   -> chown -R ec2-user -> bash /srv/ro-server/app/scripts/deploy.sh
# まで行う。出力は SSM 側で /var/log/ro-server-deploy.log に tee される。
#
# 使い方:
#   deploy.sh              通常デプロイ（イメージのビルドあり）
#   SKIP_BUILD=1 deploy.sh 設定変更のみ反映したいときにビルドを飛ばす
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"
SYSTEMD_DIR=/etc/systemd/system
SKIP_BUILD="${SKIP_BUILD:-0}"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
	sed -n '2,16p' "$0"
	exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
	echo "deploy.sh: root で実行してください" >&2
	exit 1
fi
if [ ! -d "$APP_DIR" ]; then
	echo "deploy.sh: $APP_DIR がありません" >&2
	exit 1
fi

cd "$APP_DIR"

echo "=== [1/7] ファイルのパーミッションを整える ==="
# zip 経由で配布されるため実行ビットが落ちている可能性がある
chmod 755 "$APP_DIR"/scripts/*.sh
chmod 755 "$APP_DIR"/rathena/entrypoint.sh
# sql-init/*.sh は「実行ビット無し」でないと MariaDB の initdb が source してくれない
chmod 644 "$APP_DIR"/rathena/sql-init/*
ls -l "$APP_DIR/rathena/sql-init/" | sed 's/^/    /'

echo "=== [2/7] .env の生成・同期 ==="
"$APP_DIR/scripts/init-env.sh"

echo "=== [3/7] PUBLIC_IP の取得 ==="
"$APP_DIR/scripts/update-public-ip.sh"

echo "=== [4/7] .env の権限確認 ==="
env_mode="$(stat -c '%a' "$APP_DIR/.env")"
env_owner="$(stat -c '%U' "$APP_DIR/.env")"
if [ "$env_mode" != "600" ]; then
	echo "    警告: .env が ${env_mode} だったので 600 に直します" >&2
	chmod 0600 "$APP_DIR/.env"
fi
if [ "$env_owner" != "ec2-user" ]; then
	echo "    警告: .env の所有者が ${env_owner} だったので ec2-user に直します" >&2
	chown ec2-user:ec2-user "$APP_DIR/.env"
fi
echo "    .env: $(stat -c '%U:%G %a' "$APP_DIR/.env")"

echo "=== [5/7] systemd unit の配置 ==="
install -m 0644 -o root -g root "$APP_DIR"/systemd/ro-server.service        "$SYSTEMD_DIR/"
install -m 0644 -o root -g root "$APP_DIR"/systemd/ro-server-backup.service "$SYSTEMD_DIR/"
install -m 0644 -o root -g root "$APP_DIR"/systemd/ro-server-backup.timer   "$SYSTEMD_DIR/"
systemctl daemon-reload
systemctl enable ro-server.service ro-server-backup.timer
echo "    配置・enable 完了"

echo "=== [6/7] イメージのビルド ==="
if [ "$SKIP_BUILD" = "1" ]; then
	echo "    SKIP_BUILD=1 のためビルドを飛ばします"
else
	# build args（RATHENA_COMMIT / PACKETVER）は compose が .env から補間する
	docker compose build --pull
fi

echo "=== [7/7] サービスの再起動 ==="
systemctl restart ro-server.service
systemctl start ro-server-backup.timer

echo
echo "=== status ==="
"$APP_DIR/scripts/status.sh"
