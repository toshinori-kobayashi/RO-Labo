#!/usr/bin/env bash
#
# EC2 上で MariaDB のバックアップを即時実行する（ローカル Mac 用）
# 定期バックアップは systemd ro-server-backup.timer（毎日 04:00 JST）が行う。
#
# 使い方: backup-db.sh
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,7p' "$0"; exit 0; fi

ssm_run "/srv/ro-server/app/scripts/backup-db.sh && ls -lh /srv/ro-server/backups" "ro-server backup"
