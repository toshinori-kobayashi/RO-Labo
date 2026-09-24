#!/usr/bin/env bash
#
# IMDSv2 から Public IP を取得して /srv/ro-server/app/.env の PUBLIC_IP を更新する
# （EC2 上・root 実行。systemd ro-server.service の ExecStartPre から呼ばれる）
#
# コンテナに IMDS を触らせないため、ホスト側で取得して .env に書く。
# 取得に失敗した場合は既存値を維持して警告のみ。既存値も無ければ異常終了する。
#
# 使い方: update-public-ip.sh [--help]
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"
ENV_FILE="$APP_DIR/.env"
IMDS="http://169.254.169.254"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
	sed -n '2,10p' "$0"
	exit 0
fi

if [ ! -f "$ENV_FILE" ]; then
	echo "update-public-ip.sh: $ENV_FILE がありません。先に init-env.sh を実行してください" >&2
	exit 1
fi

set_env_var() {
	local file="$1" key="$2" value="$3" tmp
	tmp="$(mktemp "${file}.XXXXXX")"
	KEY="$key" VALUE="$value" awk '
		BEGIN { key = ENVIRON["KEY"]; value = ENVIRON["VALUE"]; done = 0 }
		index($0, key "=") == 1 { if (!done) { print key "=" value; done = 1 } ; next }
		{ print }
		END { if (!done) print key "=" value }
	' "$file" > "$tmp"
	cat "$tmp" > "$file"
	rm -f "$tmp"
}

get_env_var() {
	KEY="$1" awk '
		BEGIN { key = ENVIRON["KEY"] }
		index($0, key "=") == 1 { v = substr($0, length(key) + 2) }
		END { print v }
	' "$ENV_FILE"
}

current="$(get_env_var PUBLIC_IP)"

token=""
if ! token="$(curl -fsS -m 5 -X PUT "$IMDS/latest/api/token" \
		-H 'X-aws-ec2-metadata-token-ttl-seconds: 300' 2>/dev/null)"; then
	token=""
fi

ip=""
if [ -n "$token" ]; then
	if ! ip="$(curl -fsS -m 5 -H "X-aws-ec2-metadata-token: $token" \
			"$IMDS/latest/meta-data/public-ipv4" 2>/dev/null)"; then
		ip=""
	fi
fi

if [[ ! "$ip" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
	if [ -n "$current" ]; then
		echo "update-public-ip.sh: 警告 - IMDSv2 から Public IP を取得できませんでした。既存値 ${current} を維持します" >&2
		exit 0
	fi
	echo "update-public-ip.sh: Public IP を取得できず、.env にも既存値がありません" >&2
	exit 1
fi

if [ "$ip" = "$current" ]; then
	echo "update-public-ip.sh: PUBLIC_IP は ${ip} のまま（変更なし）"
	exit 0
fi

set_env_var "$ENV_FILE" PUBLIC_IP "$ip"
chmod 0600 "$ENV_FILE"
echo "update-public-ip.sh: PUBLIC_IP を ${current:-（未設定）} -> ${ip} に更新しました"
