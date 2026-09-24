#!/usr/bin/env bash
#
# ローカル（Mac / colima）でのフレッシュ起動スモークテスト
#
# app/ を docker-compose.yml + docker-compose.local.yml でまっさらから起動し、
# map-server が NPC / マップを読み切れたかをログから機械判定する。
# NPC 翻訳ファイルを追加したあと、EC2 へ apply する前に必ず通すこと。
#
# 使い方:
#   scripts/local-smoke.sh
#   scripts/local-smoke.sh --expect-npcs 13043 --report /tmp/smoke.txt
#
# オプション:
#   --expect-npcs N   NPC 総数が N でなければ FAIL（差し替えは 1:1 なので総数は不変のはず）
#   --report PATH     画面と同じ内容を UTF-8 でファイルへ保存
#   --timeout SEC     map-server が healthy になるまでの待ち時間（既定 360 秒）
#   --keep            終了時に down しない（ログを追加調査したいとき）
#   --no-build        イメージを再ビルドしない
#
# 判定:
#   [Error] / script error / npc_parse が 1 行でもあれば FAIL
#   --expect-npcs 指定時、NPC 総数が一致しなければ FAIL
#   map-server が時間内に healthy にならなければ FAIL
#
# 前提: colima（または Docker Desktop）が起動済み。DB は ./.local/ を消して初期化する。
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
app_dir="$repo_root/app"

expect_npcs=""
report=""
timeout_sec=360
keep=0
do_build=1

while [ $# -gt 0 ]; do
	case "$1" in
		--expect-npcs) expect_npcs="${2:?--expect-npcs には数値が必要です}"; shift 2 ;;
		--report)      report="${2:?--report にはパスが必要です}"; shift 2 ;;
		--timeout)     timeout_sec="${2:?--timeout には秒数が必要です}"; shift 2 ;;
		--keep)        keep=1; shift ;;
		--no-build)    do_build=0; shift ;;
		-h|--help)     sed -n '2,30p' "$0"; exit 0 ;;
		*) echo "local-smoke.sh: 不明な引数: $1" >&2; exit 2 ;;
	esac
done

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/local-smoke.XXXXXX")"
out_file="$tmp_dir/report.txt"
log_file="$tmp_dir/map-server.log"

say() { printf '%s\n' "$*" | tee -a "$out_file"; }

compose() {
	docker compose -f docker-compose.yml -f docker-compose.local.yml "$@"
}

cleanup() {
	local rc=$?
	if [ "$keep" -eq 0 ]; then
		( cd "$app_dir" && compose down --remove-orphans >/dev/null 2>&1 ) || true
	fi
	if [ -n "$report" ] && [ -f "$out_file" ]; then
		mkdir -p "$(dirname "$report")"
		cp "$out_file" "$report"
		echo "レポート: $report"
	fi
	rm -rf "$tmp_dir"
	exit $rc
}
trap cleanup EXIT

started_at="$(date +%s)"

say "=================================================================="
say " ro-server ローカルスモークテスト"
say " 開始      : $(date '+%Y-%m-%d %H:%M:%S')"
say " app       : $app_dir"
say " 期待 NPC  : ${expect_npcs:-（指定なし）}"
say "=================================================================="
say ""

cd "$app_dir"

# ---- .env ----------------------------------------------------------------
if [ ! -f .env ]; then
	cp .env.local.example .env
	say "[setup] .env が無いので .env.local.example からコピーしました"
else
	say "[setup] 既存の .env を使います"
fi

# ---- 前回の残骸を落とす --------------------------------------------------
compose down --remove-orphans >/dev/null 2>&1 || true

# ---- DB を初期化（./.local/ を削除） -------------------------------------
if [ -d .local ]; then
	if ! rm -rf .local 2>/dev/null; then
		# コンテナが root で作ったファイルはホストから消せないことがある
		docker run --rm -v "$app_dir/.local:/target" alpine:3 \
			sh -c 'rm -rf /target/* /target/.[!.]* /target/..?* 2>/dev/null || true' >/dev/null 2>&1 || true
		rm -rf .local
	fi
	say "[setup] ./.local/ を削除しました（DB を初期化）"
else
	say "[setup] ./.local/ は元から存在しません（DB は新規作成）"
fi

# ---- 起動 ----------------------------------------------------------------
build_flag=""
[ "$do_build" -eq 1 ] && build_flag="--build"
say "[up] docker compose up -d ${build_flag}"
build_log="$tmp_dir/build.log"
if ! compose up -d $build_flag >"$build_log" 2>&1; then
	say "[up] FAIL: 起動に失敗しました"
	# overlay-utf8 の CP932 変換で落ちるのが一番多いので、その行だけ先に抜き出す
	# （Dockerfile 本文のエコー ">>>" は除外する）
	overlay_err="$(grep -E 'overlay-utf8/|overlay: |CP932 に変換できない|UTF-8 BOM|波ダッシュ' "$build_log" \
		| grep -v -F '>>>' | grep -v -F 'RUN set -eu' | head -n 40 || true)"
	if [ -n "$overlay_err" ]; then
		say "---- overlay-utf8 の変換エラー ----"
		printf '%s\n' "$overlay_err" | sed 's/^/    /' | tee -a "$out_file"
		say "    （scripts/check-overlay.sh で手元でも同じ検査ができます）"
	fi
	say "---- docker compose 出力（末尾 30 行） ----"
	tail -n 30 "$build_log" | sed 's/^/    /' | tee -a "$out_file"
	# ビルドは通ったが依存サービスが unhealthy で落ちた場合に備えて各サービスの末尾も出す
	for svc in mariadb login-server char-server map-server; do
		svc_log="$(compose logs --no-color --tail 12 "$svc" 2>/dev/null || true)"
		if [ -n "$svc_log" ]; then
			say "---- ${svc}（末尾 12 行） ----"
			printf '%s\n' "$svc_log" | sed 's/^/    /' | tee -a "$out_file"
		fi
	done
	say ""
	say "結果: FAIL"
	exit 1
fi
say "[up] 起動コマンド成功（ビルドログ ${build_log##*/}: $(wc -l < "$build_log" | tr -d ' ') 行）"

# ---- map-server が healthy になるまで待つ --------------------------------
say "[wait] map-server が healthy になるまで待機（最大 ${timeout_sec} 秒）"
deadline=$(( started_at + timeout_sec + 30 ))
health="unknown"
while :; do
	cid="$(compose ps -q map-server 2>/dev/null || true)"
	if [ -n "$cid" ]; then
		state="$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || echo unknown)"
		health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null || echo unknown)"
		if [ "$health" = "healthy" ]; then
			break
		fi
		if [ "$state" = "exited" ] || [ "$state" = "dead" ]; then
			health="exited"
			break
		fi
	fi
	if [ "$(date +%s)" -ge "$deadline" ]; then
		health="timeout"
		break
	fi
	sleep 5
done
elapsed=$(( $(date +%s) - started_at ))
say "[wait] map-server: ${health}（${elapsed} 秒）"

# ---- ログ収集 ------------------------------------------------------------
compose logs --no-color --no-log-prefix map-server > "$log_file" 2>/dev/null \
	|| compose logs --no-color map-server > "$log_file" 2>/dev/null || true

fail=0
say ""
say "---------------- 読み込み結果 ----------------"

npc_total=""
npc_block="$(grep -A 7 -E "Done loading '[0-9]+' NPCs" "$log_file" | grep -v '^--$' || true)"
if [ -n "$npc_block" ]; then
	printf '%s\n' "$npc_block" | sed 's/^/  /' | tee -a "$out_file"
	npc_total="$(printf '%s\n' "$npc_block" | sed -n "s/.*Done loading '\([0-9]*\)' NPCs.*/\1/p" | head -1)"
else
	say "  (NPC 読み込み行が見つかりません)"
fi

maps_line="$(grep -F "Successfully loaded '" "$log_file" | head -1 || true)"
if [ -n "$maps_line" ]; then
	say "  ${maps_line#*: }"
else
	say "  (マップ読み込み行が見つかりません)"
fi

mob_line="$(grep -F "db/import/mob_db.yml" "$log_file" | grep -F "Done reading" | head -1 || true)"
say "  mob_db.yml       : ${mob_line:-（行なし）}"

msg_line="$(grep -F "map_msg_eng_conf.txt" "$log_file" | grep -F "Done reading" | head -1 || true)"
say "  map_msg_eng_conf : ${msg_line:-（行なし）}"

# ---- エラー / 警告 -------------------------------------------------------
err_file="$tmp_dir/errors.txt"
# [Info] 行（例: npc_parse_function: Overwriting user function — 翻訳版 Global_Functions が同名関数を上書きする正常動作）は数えない
grep -E -i '\[Error\]|script error|npc_parse' "$log_file" | grep -v '^\[Info\]' > "$err_file" || true
err_count="$(wc -l < "$err_file" | tr -d ' ')"

warn_file="$tmp_dir/warnings.txt"
grep -F '[Warning]' "$log_file" | grep -v -F 'mesitemicon' > "$warn_file" || true
warn_count="$(wc -l < "$warn_file" | tr -d ' ')"

say ""
say "---------------- エラー / 警告 ----------------"
say "  [Error] / script error / npc_parse : ${err_count} 行"
if [ "$err_count" -gt 0 ]; then
	sed 's/^/    /' "$err_file" | tee -a "$out_file"
	fail=1
fi
say "  [Warning]（mesitemicon 以外）      : ${warn_count} 行"
if [ "$warn_count" -gt 0 ]; then
	sed 's/^/    /' "$warn_file" | tee -a "$out_file"
fi

# ---- 判定 ----------------------------------------------------------------
say ""
say "---------------- 判定 ----------------"

if [ "$health" != "healthy" ]; then
	say "  NG: map-server が healthy になりませんでした（${health}）"
	say "      （ログ末尾 20 行）"
	tail -n 20 "$log_file" | sed 's/^/      /' | tee -a "$out_file"
	fail=1
else
	say "  OK: map-server healthy"
fi

if [ "$err_count" -gt 0 ]; then
	say "  NG: エラー行あり（${err_count} 行）"
else
	say "  OK: [Error] / script error / npc_parse は 0 行"
fi

if [ -n "$expect_npcs" ]; then
	if [ -z "$npc_total" ]; then
		say "  NG: NPC 総数を取得できませんでした（期待 ${expect_npcs}）"
		fail=1
	elif [ "$npc_total" != "$expect_npcs" ]; then
		say "  NG: NPC 総数が一致しません（実測 ${npc_total} / 期待 ${expect_npcs}）"
		fail=1
	else
		say "  OK: NPC 総数 ${npc_total} = 期待値"
	fi
else
	say "  --: NPC 総数 ${npc_total:-不明}（--expect-npcs 未指定）"
fi

total_elapsed=$(( $(date +%s) - started_at ))
say ""
if [ "$fail" -eq 0 ]; then
	say "結果: PASS（所要 ${total_elapsed} 秒）"
else
	say "結果: FAIL（所要 ${total_elapsed} 秒）"
fi

exit "$fail"
