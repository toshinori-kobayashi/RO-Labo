# Amazon Linux 2023 x86_64 の最新 AMI（AWS 公開 SSM パラメータ）
data "aws_ssm_parameter" "al2023" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

# 実行中のアカウント確認用（誤ったアカウントへの apply を plan 時に気付けるようにする）
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# アプリ一式（../app）を zip 化してデプロイ用バケットへ置く。
# ※ ../app が存在しないと plan 時点でエラーになる。
data "archive_file" "app" {
  type        = "zip"
  source_dir  = "${path.module}/../app"
  output_path = "${path.module}/.build/app.zip"
  excludes    = [".env", ".local", ".local/**"]
}
