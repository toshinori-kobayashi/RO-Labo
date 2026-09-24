output "instance_id" {
  description = "アプリケーションサーバの EC2 インスタンス ID"
  value       = aws_instance.app.id
}

output "public_ip" {
  description = "クライアントへ配布する固定 Public IP（EIP）"
  value       = aws_eip.app.public_ip
}

output "public_dns" {
  description = "EIP の Public DNS 名"
  value       = aws_eip.app.public_dns
}

output "data_volume_id" {
  description = "データ用 EBS のボリューム ID"
  value       = aws_ebs_volume.data.id
}

output "security_group_id" {
  description = "アプリケーションサーバのセキュリティグループ ID"
  value       = aws_security_group.app.id
}

output "log_group_name" {
  description = "コンテナログの CloudWatch ロググループ名"
  value       = aws_cloudwatch_log_group.containers.name
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "subnet_id" {
  description = "Public Subnet ID"
  value       = aws_subnet.public.id
}

output "deploy_bucket" {
  description = "アプリ配布用 S3 バケット名"
  value       = aws_s3_bucket.deploy.id
}

output "ssm_association_id" {
  description = "デプロイ用 SSM Association の ID"
  value       = aws_ssm_association.app_deploy.association_id
}

output "dlm_policy_id" {
  description = "data EBS スナップショットの DLM ポリシー ID"
  value       = aws_dlm_lifecycle_policy.data.id
}

output "ssm_start_session_command" {
  description = "Session Manager でシェルに入るコマンド"
  value       = "aws --profile ${var.profile} ssm start-session --target ${aws_instance.app.id}"
}

output "ssm_association_status_command" {
  description = "デプロイ（SSM Association）の実行状況を確認するコマンド"
  value       = "aws --profile ${var.profile} --region ${var.region} ssm describe-association-executions --association-id ${aws_ssm_association.app_deploy.association_id}"
}

output "ssm_deploy_log_command" {
  description = "SSM 実行ログ（S3 出力）の一覧を確認するコマンド"
  value       = "aws --profile ${var.profile} --region ${var.region} s3 ls s3://${aws_s3_bucket.deploy.id}/${local.ssm_output_prefix}/ --recursive"
}
