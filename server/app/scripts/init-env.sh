#!/usr/bin/env bash
#
# /srv/ro-server/app/.env を冪等に用意する（EC2 上・root 実行）
#
#   - .env が無ければ秘密情報を生成して新規作成
#   - .env があれば config.env 由来のキーだけを同期し、秘密情報と PUBLIC_IP は保持
#   - 生成する秘密は openssl rand ベースの英数字のみ
#     （rAthena の userid/passwd は 23 文字上限、sql-init の正規表現検証も英数字のみ）
#
# 注意: .env を消して作り直すと DB のパスワードだけ新しくなり、既存の
#       /srv/ro-server/mariadb（初期化済み）と食い違って起動しなくなる。
#       作り直す場合は DB も初期化するか、旧 .env から秘密を復元すること。
#
# 使い方: init-env.sh [--help]
#
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/ro-server/app}"
CONFIG_ENV="$APP_DIR/config.env"
ENV_FILE="$APP_DIR/.env"
ENV_OWNER="${ENV_OWNER:-ec2-user}"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
	sed -n '2,12p' "$0"
	exit 0
fi

if [ "$(id -u)" -ne 0 ]; then
	echo "init-env.sh: root で実行してください" >&2
	exit 1
fi
if [ ! -f "$CONFIG_ENV" ]; then
	echo "init-env.sh: $CONFIG_ENV がありません" >&2
	exit 1
fi

# 英数字のみの乱数文字列を生成する（head を使わず SIGPIPE を避ける）
gen_alnum() {
	local want="$1" out=""
	while [ "${#out}" -lt "$want" ]; do
		out="${out}$(openssl rand -base64 48 | LC_ALL=C tr -dc 'A-Za-z0-9')"
	done
	printf '%s' "${out:0:want}"
}

# .env の KEY= 行を置換、無ければ追記（値に記号が入っても壊れないよう awk で処理）
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
	[ -f "$ENV_FILE" ] || return 0
	KEY="$1" awk '
		BEGIN { key = ENVIRON["KEY"] }
		index($0, key "=") == 1 { v = substr($0, length(key) + 2) }
		END { print v }
	' "$ENV_FILE"
}

umask 077
if [ ! -f "$ENV_FILE" ]; then
	echo "init-env.sh: $ENV_FILE を新規作成します"
	: > "$ENV_FILE"
fi
chmod 0600 "$ENV_FILE"

# --- config.env のキーを同期 -------------------------------------------------
synced=0
while IFS= read -r line; do
	case "$line" in
		''|'#'*) continue ;;
	esac
	case "$line" in
		*=*) ;;
		*) continue ;;
	esac
	key="${line%%=*}"
	value="${line#*=}"
	set_env_var "$ENV_FILE" "$key" "$value"
	synced=$((synced + 1))
done < "$CONFIG_ENV"
echo "init-env.sh: config.env から ${synced} 件のキーを同期しました"

# --- 秘密情報（未設定のときだけ生成） ----------------------------------------
generated=()
if [ -z "$(get_env_var MARIADB_ROOT_PASSWORD)" ]; then
	set_env_var "$ENV_FILE" MARIADB_ROOT_PASSWORD "$(gen_alnum 32)"
	generated+=(MARIADB_ROOT_PASSWORD)
fi
if [ -z "$(get_env_var MARIADB_PASSWORD)" ]; then
	set_env_var "$ENV_FILE" MARIADB_PASSWORD "$(gen_alnum 32)"
	generated+=(MARIADB_PASSWORD)
fi
# inter-server 認証: rAthena の login.userid は varchar(23)
if [ -z "$(get_env_var INTERSERVER_USER)" ]; then
	set_env_var "$ENV_FILE" INTERSERVER_USER "s_$(gen_alnum 8)"
	generated+=(INTERSERVER_USER)
fi
if [ -z "$(get_env_var INTERSERVER_PASSWORD)" ]; then
	set_env_var "$ENV_FILE" INTERSERVER_PASSWORD "$(gen_alnum 20)"
	generated+=(INTERSERVER_PASSWORD)
fi

# PUBLIC_IP の行だけ用意しておく（値は update-public-ip.sh が入れる）
if [ -z "$(get_env_var PUBLIC_IP)" ]; then
	set_env_var "$ENV_FILE" PUBLIC_IP ""
fi

if [ "${#generated[@]}" -gt 0 ]; then
	echo "init-env.sh: 秘密情報を生成しました: ${generated[*]}"
	echo "init-env.sh: 値は $ENV_FILE にのみ保存されます（表示しません）"
else
	echo "init-env.sh: 既存の秘密情報を保持しました"
fi

chown "${ENV_OWNER}:${ENV_OWNER}" "$ENV_FILE" 2>/dev/null || true
chmod 0600 "$ENV_FILE"
echo "init-env.sh: 完了 ($(stat -c '%U:%G %a' "$ENV_FILE") $ENV_FILE)"
