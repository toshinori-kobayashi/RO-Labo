# アプリ配布用バケット。中身は apply のたびに Terraform が再アップロードする
# 一時置き場なので、Sandbox の aws-nuke が毎晩 S3Object を削除しても実害はない。
# （バケット自体は DoNotNuke タグで保護される）
# 公開ブロック（Public Access Block）は S3 の新規バケット既定で全項目が有効になっており、
# この Sandbox では SCP により s3:PutBucketPublicAccessBlock が拒否されるため、
# aws_s3_bucket_public_access_block は宣言しない（実効状態は get-public-access-block で全 true を確認済み）。
resource "aws_s3_bucket" "deploy" {
  bucket        = local.names.deploy_bucket
  force_destroy = true

  tags = {
    Name = local.names.deploy_bucket
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "deploy" {
  bucket = aws_s3_bucket.deploy.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "app" {
  bucket = aws_s3_bucket.deploy.id
  key    = local.deploy_object_key
  source = data.archive_file.app.output_path

  # 中身が変わったら再アップロードする
  source_hash = data.archive_file.app.output_md5

  tags = {
    Name = local.names.app_bundle
  }
}

# デプロイは SSM Association で行う（SSH / rsync 経路を持たない）。
# commands にバンドルの md5 が含まれるため、app の内容が変わると association が
# 更新され、自動的に再実行される。
resource "aws_ssm_association" "app_deploy" {
  name             = "AWS-RunShellScript"
  association_name = local.names.ssm_association

  targets {
    key    = "InstanceIds"
    values = [aws_instance.app.id]
  }

  parameters = {
    commands = templatefile("${path.module}/templates/ssm_deploy.sh.tftpl", {
      bucket  = aws_s3_bucket.deploy.id
      key     = local.deploy_object_key
      md5     = data.archive_file.app.output_md5
      app_dir = local.app_dir
    })
    executionTimeout = "3600"
  }

  output_location {
    s3_bucket_name = aws_s3_bucket.deploy.id
    s3_key_prefix  = local.ssm_output_prefix
  }

  wait_for_success_timeout_seconds = 3000

  tags = {
    Name = local.names.ssm_association
  }

  depends_on = [
    aws_s3_object.app,
    aws_volume_attachment.data,
    aws_eip_association.app,
    aws_iam_role_policy.ec2_inline,
    aws_iam_role_policy_attachment.ssm_core,
  ]
}
