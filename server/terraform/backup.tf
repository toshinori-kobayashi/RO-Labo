# data EBS の日次スナップショット（7 世代）。
# 19:30 UTC = 04:30 JST。DlmBackup タグが付いたボリュームのみ対象。
resource "aws_dlm_lifecycle_policy" "data" {
  description        = local.names.dlm_policy
  execution_role_arn = aws_iam_role.dlm.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]

    target_tags = {
      DlmBackup = local.names.dlm_target
    }

    schedule {
      name = "daily-${var.snapshot_retain_count}d"

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = [var.snapshot_time_utc]
      }

      retain_rule {
        count = var.snapshot_retain_count
      }

      # copy_tags = true にすると元ボリュームの Name / DoNotNuke 等と tags_to_add のキーが
      # 重複し、CreateSnapshot が "Duplicate tag key 'Name' specified" で失敗して
      # ポリシーが ERROR になる（2026-09-22 19:54Z の初回実行で発生）。
      # そのためコピーはせず、必要なタグ（DoNotNuke 含む共通 7 タグ + Name）を明示的に付ける。
      copy_tags = false

      tags_to_add = merge(local.common_tags, {
        Name = local.names.data_snapshot
      })
    }
  }

  tags = {
    Name = local.names.dlm_policy
  }

  depends_on = [aws_iam_role_policy_attachment.dlm]
}
