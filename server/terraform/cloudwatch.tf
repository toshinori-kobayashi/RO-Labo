resource "aws_cloudwatch_log_group" "containers" {
  name              = local.names.log_group
  retention_in_days = var.log_retention_days

  tags = {
    Name = local.names.log_group
  }
}

# システムステータスチェック失敗 -> EC2 自動復旧（通知先なし）
resource "aws_cloudwatch_metric_alarm" "status_check" {
  alarm_name          = local.names.alarm
  alarm_description   = "StatusCheckFailed_System for ${local.names.instance}: trigger EC2 auto recovery"
  namespace           = "AWS/EC2"
  metric_name         = "StatusCheckFailed_System"
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 2
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "missing"

  dimensions = {
    InstanceId = aws_instance.app.id
  }

  alarm_actions = ["arn:aws:automate:${data.aws_region.current.region}:ec2:recover"]

  tags = {
    Name = local.names.alarm
  }
}
