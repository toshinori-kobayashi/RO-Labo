#!/usr/bin/env bash
#
# SSM Session Manager で EC2 の対話シェルに入る（ローカル Mac 用）
#
# 使い方: ssm-shell.sh [--help]
#
# 前提: session-manager-plugin（brew install --cask session-manager-plugin）
# 入った後の定番操作:
#   sudo -i
#   cd /opt/ro-server && docker compose ps
#
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then sed -n '2,12p' "$0"; exit 0; fi

require_tools aws session-manager-plugin
iid="$(instance_id)"
info "start-session -> $iid (profile: $AWS_PROFILE / region: $REGION)"
exec aws --profile "$AWS_PROFILE" --region "$REGION" ssm start-session --target "$iid"
