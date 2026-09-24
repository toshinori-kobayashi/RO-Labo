#!/usr/bin/env bash
#
# コンテナの状態と、各サーバの起動ログの要点を表示する（EC2 上・root 実行）
#
# 使い方: status.sh [--tail N]   （既定 N=2000）
#
# grep する文字列は rAthena の実ソース（RATHENA_COMMIT のコミット）に合わせている:
#   login: src/login/login.cpp:907          "The login-server is ready ..."
#          src/login/loginclif.cpp:432      "Connection of the char-server '%s' accepted."
#   char : src/char/char_logif.cpp:285      "Connected to login-server (connection #%d)."
#          src/char/char.cpp:3288           "The char-server is ready ..."
#          src/char/char.cpp:2574           "DB integrity check finished with success"
#   map  : src/map/map.cpp:4414             "Connect success! (Map Server Connection)"
#          src/map/map.cpp:3928             "Loading maps (using %s as map cache)..."  ← pre-re か re かがわかる
#          src/map/map.cpp:4031             "Successfully loaded '%d' maps."
#          src/map/npc.cpp:3656             "Done loading '%d' NPCs:"
#          src/map/chrif.cpp:488            "Successfully logged on to Char Server ..."
#          src/map/map.cpp:5456             "Server is 'ready' and listening on port '%d'."
# 色コードは stdout_with_ansisequence: no のため出力時に除去される（src/common/showmsg.cpp:539）。
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"
TAIL=2000

while [ $# -gt 0 ]; do
	case "$1" in
		--tail) TAIL="${2:?--tail には行数が必要です}"; shift 2 ;;
		-h|--help) sed -n '2,20p' "$0"; exit 0 ;;
		*) echo "status.sh: 不明な引数: $1" >&2; exit 1 ;;
	esac
done

cd "$APP_DIR"

echo "==================== docker compose ps ===================="
docker compose ps
echo

show() {
	local service="$1" pattern="$2" after="${3:-0}" out
	echo "==================== ${service} ===================="
	out="$(docker compose logs --no-color --tail "$TAIL" "$service" 2>/dev/null \
		| grep -E -A "$after" "$pattern" || true)"
	if [ -n "$out" ]; then
		printf '%s\n' "$out" | tail -n 40
	else
		echo "  (該当するログ行が見つかりません。docker compose logs ${service} を直接確認してください)"
	fi
	echo
}

show login-server \
	'The login-server is|Connection of the char-server|Couldn.t connect with uname=|\[Error\]|\[SQL\]'

show char-server \
	'Connected to login-server|The char-server is|DB integrity check finished|Connection to Login Server lost|\[Error\]'

show map-server \
	'Connect success!|Loading maps \(using|Successfully loaded|Done loading|Successfully logged on to Char Server|Server is .ready.|Connection to char-server failed|\[Error\]' 6

# ---- NPC 差し替え（overlay-utf8）の構文エラー検知 ----
# 日本語版 NPC に差し替えた結果パースに失敗していないかを件数で見る。
#   script error  : src/map/script.cpp の disp_error_message 系（スクリプト構文エラー）
#   npc_parse     : src/map/npc.cpp の npc_parse_* 系エラー（NPC 定義行の解析失敗、
#                   npc_parsesrcfile: File not found を含む）
#   Unknown       : conf の未知キー（map.cpp:4248 "Unknown setting"）や不明な定数
# いずれも 0 でなければ docker compose logs map-server を直接見ること。
echo "==================== map-server NPC パース ===================="
npc_log="$(docker compose logs --no-color --tail "$TAIL" map-server 2>/dev/null || true)"
for pat in 'script error' 'npc_parse' 'Unknown'; do
	cnt="$(printf '%s\n' "$npc_log" | grep -c -F "$pat" || true)"
	printf '  %-14s %s 行\n' "$pat" "${cnt:-0}"
done
printf '%s\n' "$npc_log" | grep -E -i 'script error|npc_parse|Unknown' | tail -n 20 || true
echo

echo "==================== mariadb ===================="
docker compose logs --no-color --tail 50 mariadb 2>/dev/null | tail -n 20
echo

echo "==================== systemd ===================="
systemctl is-active ro-server.service  || true
systemctl is-enabled ro-server.service || true
systemctl is-active ro-server-backup.timer  || true
systemctl list-timers --no-pager ro-server-backup.timer 2>/dev/null || true
