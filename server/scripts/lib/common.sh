#!/usr/bin/env bash
#
# ローカル Mac 用スクリプトの共通関数。各スクリプトから source して使う。
#
# 前提: AWS SSO (`aws sso login --profile sandbox-power`) 済み。
#       EC2 へは SSM 経由でのみアクセスする（SSH / 22 番は使わない）。
#
# 環境変数で上書きできるもの:
#   AWS_PROFILE     既定 sandbox-power
#   AWS_DEFAULT_REGION / REGION  既定 ap-northeast-1
#   RO_INSTANCE_ID  terraform output を使わずインスタンス ID を直接指定
#   RO_PUBLIC_IP    同上（Public IP）
#   RO_LOG_GROUP    同上（CloudWatch Logs ロググループ）
#

AWS_PROFILE="${AWS_PROFILE:-sandbox-power}"
REGION="${REGION:-${AWS_DEFAULT_REGION:-ap-northeast-1}}"

# このファイルは <repo>/scripts/lib/common.sh にある
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TF_DIR="$REPO_ROOT/terraform"

die() { echo "エラー: $*" >&2; exit 1; }
info() { echo "==> $*" >&2; }

require_tools() {
	local t missing=()
	for t in "$@"; do
		command -v "$t" >/dev/null 2>&1 || missing+=("$t")
	done
	if [ "${#missing[@]}" -gt 0 ]; then
		die "次のコマンドが見つかりません: ${missing[*]}"
	fi
}

aws_() {
	command aws --profile "$AWS_PROFILE" --region "$REGION" "$@"
}

_tf_output() {
	local name="$1"
	[ -d "$TF_DIR" ] || die "$TF_DIR がありません"
	terraform -chdir="$TF_DIR" output -raw "$name" 2>/dev/null \
		|| die "terraform output '${name}' を取得できませんでした（terraform apply 済みか確認してください）"
}

_INSTANCE_ID=""
instance_id() {
	if [ -n "${RO_INSTANCE_ID:-}" ]; then printf '%s' "$RO_INSTANCE_ID"; return; fi
	if [ -z "$_INSTANCE_ID" ]; then
		require_tools terraform
		_INSTANCE_ID="$(_tf_output instance_id)"
	fi
	printf '%s' "$_INSTANCE_ID"
}

_PUBLIC_IP=""
public_ip() {
	if [ -n "${RO_PUBLIC_IP:-}" ]; then printf '%s' "$RO_PUBLIC_IP"; return; fi
	if [ -z "$_PUBLIC_IP" ]; then
		require_tools terraform
		_PUBLIC_IP="$(_tf_output public_ip)"
	fi
	printf '%s' "$_PUBLIC_IP"
}

_LOG_GROUP=""
log_group() {
	if [ -n "${RO_LOG_GROUP:-}" ]; then printf '%s' "$RO_LOG_GROUP"; return; fi
	if [ -z "$_LOG_GROUP" ]; then
		require_tools terraform
		_LOG_GROUP="$(_tf_output log_group_name)"
	fi
	printf '%s' "$_LOG_GROUP"
}

# ssm_run "<shell command>"
#   AWS-RunShellScript で EC2 上のコマンドを実行し、標準出力／標準エラーを表示する。
#   SSM Agent はコマンドを root として実行するので sudo は不要。
#   失敗時は非 0 で終了する。
#   注意: get-command-invocation の出力は 24000 文字で打ち切られる。
#         長いログは scripts/logs.sh（CloudWatch Logs）を使うこと。
ssm_run() {
	local cmd="${1:?ssm_run: 実行するコマンドを指定してください}"
	local comment="${2:-ro-server}"
	require_tools aws python3
	local iid params cid status rc
	iid="$(instance_id)"

	params="$(mktemp -t ro-ssm-params)"
	CMD="$cmd" python3 -c 'import json,os,sys; json.dump({"commands":[os.environ["CMD"]]}, sys.stdout)' > "$params"

	cid="$(aws_ ssm send-command \
		--instance-ids "$iid" \
		--document-name AWS-RunShellScript \
		--comment "${comment:0:100}" \
		--timeout-seconds 3600 \
		--parameters "file://$params" \
		--query 'Command.CommandId' --output text)" || { rm -f "$params"; die "send-command に失敗しました"; }
	rm -f "$params"

	info "SSM CommandId: $cid (instance: $iid)"

	# 送信直後は InvocationDoesNotExist になることがあるので少し待ってから wait する
	local i
	for i in 1 2 3 4 5; do
		if aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$iid" \
				--query 'Status' --output text >/dev/null 2>&1; then
			break
		fi
		sleep 2
	done
	aws_ ssm wait command-executed --command-id "$cid" --instance-id "$iid" >/dev/null 2>&1 || true

	status="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$iid" \
		--query 'Status' --output text)"
	rc="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$iid" \
		--query 'ResponseCode' --output text)"

	local stdout stderr
	stdout="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$iid" \
		--query 'StandardOutputContent' --output text)"
	stderr="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$iid" \
		--query 'StandardErrorContent' --output text)"

	if [ -n "$stdout" ] && [ "$stdout" != "None" ]; then
		printf '%s\n' "$stdout"
	fi
	if [ -n "$stderr" ] && [ "$stderr" != "None" ]; then
		echo "----- stderr -----" >&2
		printf '%s\n' "$stderr" >&2
	fi

	info "Status: ${status} (ResponseCode: ${rc})"
	if [ "$status" != "Success" ]; then
		return 1
	fi
	return 0
}

# シングルクォートで囲む用のエスケープ
shq() { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
