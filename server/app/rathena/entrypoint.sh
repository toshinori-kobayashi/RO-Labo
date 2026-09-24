#!/usr/bin/env bash
#
# rAthena サーバ起動用 entrypoint
#
# 使い方: entrypoint.sh <login|char|map>
#   conf/import/*.tmpl を環境変数で描画してから該当サーバをフォアグラウンド起動する。
#   PID 1 は compose の init: true（tini）が担当するため exec でそのまま置き換える。
#
# 必須環境変数:
#   PUBLIC_IP INTERSERVER_USER INTERSERVER_PASSWORD
#   MARIADB_USER MARIADB_PASSWORD MARIADB_DATABASE SERVER_NAME
#
set -euo pipefail

usage() {
  echo "usage: $0 <login|char|map>" >&2
}

role="${1:-}"
case "$role" in
  login|char|map) ;;
  -h|--help) usage; exit 0 ;;
  *) usage; exit 1 ;;
esac

# 描画に使う変数。envsubst にはこの一覧だけを渡し、
# conf 内の他の $ 表記を巻き込まないようにする。
REQUIRED_VARS=(
  PUBLIC_IP
  INTERSERVER_USER
  INTERSERVER_PASSWORD
  MARIADB_USER
  MARIADB_PASSWORD
  MARIADB_DATABASE
  SERVER_NAME
)

missing=()
for v in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!v:-}" ]; then
    missing+=("$v")
  fi
done
if [ "${#missing[@]}" -gt 0 ]; then
  echo "entrypoint: 必須環境変数が未設定です: ${missing[*]}" >&2
  exit 1
fi

SUBST_VARS=''
for v in "${REQUIRED_VARS[@]}"; do
  SUBST_VARS="${SUBST_VARS}\${${v}} "
done

cd /opt/rathena

# conf/import/*.tmpl -> conf/import/*（.tmpl を除いた名前）
# 描画結果には inter-server / DB のパスワードが入るので内容はログに出さない。
shopt -s nullglob
old_umask="$(umask)"
umask 077
for tmpl in conf/import/*.tmpl; do
  out="${tmpl%.tmpl}"
  envsubst "$SUBST_VARS" < "$tmpl" > "$out"
  echo "entrypoint: rendered ${out}"
done
umask "$old_umask"
shopt -u nullglob

# ------------------------------------------------------------------
# コンソールログの CP932 -> UTF-8 変換
# ------------------------------------------------------------------
# rAthena はキャラ名・ギルド名・Mob 名などを CP932 のまま stdout / stderr へ出す
# （文字列をバイト列として素通しするため）。そのままだと awslogs 経由で
# CloudWatch Logs に入ったときに文字化けするので、出力だけを UTF-8 へ変換する。
#
# 注意: glibc の iconv(1) をそのままパイプに挟んではいけない。
#       パイプ入力の場合 iconv は EOF まで全部読んでから変換するため
#       （検証済み: 200KB 流しても EOF まで 1 バイトも出てこない）、
#       ログがサーバ終了時までまとめて出る状態になる。
#       そこで 1 行ずつ読み、非 ASCII バイトを含む行だけ iconv に通す。
#       rAthena のログはほぼ ASCII なのでプロセス生成は日本語を含む行だけになる
#       （実測: ASCII 5000 行で 0.06 秒、非 ASCII 500 行で 0.17 秒）。
#
# プロセス置換 > >(...) でパイプを張ってから exec するため、サーバ本体は
# このシェルを置き換える形で起動する。PID は変わらないので compose の
# init: true（tini）からの SIGTERM はサーバへ直接届き、graceful shutdown を壊さない。
# 変換対象は stdout / stderr だけで、healthcheck（TCP 接続）には影響しない。
cp932_to_utf8() {
  local line
  # read が失敗しても $line が空でなければ最終行（改行なし）として処理する
  while IFS= read -r line || [ -n "$line" ]; do
    # 非 ASCII バイトを含む行だけ変換する。
    # || true は set -e 対策。ここでフィルタが落ちるとサーバが SIGPIPE で死ぬ。
    case "$line" in
      *[$'\x80'-$'\xff']*) printf '%s\n' "$line" | iconv -c -f CP932 -t UTF-8 || true ;;
      *)                    printf '%s\n' "$line" ;;
    esac
  done
}

# iconv は libc-bin 同梱。念のため無い場合は変換なしで起動する（ログのためにサーバを止めない）。
if ! command -v iconv >/dev/null 2>&1; then
  echo "entrypoint: iconv が見つからないためログ変換なしで起動します" >&2
  echo "entrypoint: starting ${role}-server (PACKETVER build / Pre-Renewal)"
  exec "./${role}-server"
fi

echo "entrypoint: starting ${role}-server (PACKETVER build / Pre-Renewal, console log CP932 -> UTF-8)"
exec "./${role}-server" > >(cp932_to_utf8) 2>&1
