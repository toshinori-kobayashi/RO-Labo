# --- EC2 インスタンスロール ---

data "aws_iam_policy_document" "ec2_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ec2" {
  name               = local.names.ec2_role
  description        = "Instance role for ${local.names.instance}"
  assume_role_policy = data.aws_iam_policy_document.ec2_assume_role.json

  tags = {
    Name = local.names.ec2_role
  }
}

# Session Manager / SSM Association 実行用（Inbound 22 を開けないための必須要素）
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# docker awslogs driver 用（対象ロググループ限定）＋ デプロイバンドルの取得と
# SSM 実行ログの書き出し（対象バケット限定）
data "aws_iam_policy_document" "ec2_inline" {
  statement {
    sid    = "WriteContainerLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
    ]

    resources = [
      aws_cloudwatch_log_group.containers.arn,
      "${aws_cloudwatch_log_group.containers.arn}:*",
    ]
  }

  statement {
    sid       = "GetDeployBundle"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.deploy.arn}/${local.deploy_object_key}"]
  }

  statement {
    sid       = "PutSsmOutput"
    effect    = "Allow"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.deploy.arn}/${local.ssm_output_prefix}/*"]
  }

  # ListBucket に加え、SSM Agent が S3 出力先の暗号化設定を確認するため
  # GetEncryptionConfiguration も許可する
  statement {
    sid    = "InspectDeployBucket"
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:GetEncryptionConfiguration",
    ]

    resources = [aws_s3_bucket.deploy.arn]
  }
}

resource "aws_iam_role_policy" "ec2_inline" {
  name   = local.names.cwlogs_policy
  role   = aws_iam_role.ec2.id
  policy = data.aws_iam_policy_document.ec2_inline.json
}

resource "aws_iam_instance_profile" "ec2" {
  name = local.names.ec2_role
  role = aws_iam_role.ec2.name

  tags = {
    Name = local.names.ec2_role
  }
}

# --- DLM（EBS スナップショット）用ロール ---

data "aws_iam_policy_document" "dlm_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["dlm.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dlm" {
  name               = local.names.dlm_role
  description        = "Execution role for ${local.names.dlm_policy}"
  assume_role_policy = data.aws_iam_policy_document.dlm_assume_role.json

  tags = {
    Name = local.names.dlm_role
  }
}

resource "aws_iam_role_policy_attachment" "dlm" {
  role       = aws_iam_role.dlm.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSDataLifecycleManagerServiceRole"
}
