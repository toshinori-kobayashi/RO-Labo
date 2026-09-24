locals {
  project_name = var.project_name
  environment  = var.environment

  # リソース名は全てこのフォーマットから組み立てる（個別ハードコードしない）
  name_fmt = "${local.project_name}-%s-${local.environment}"

  # provider default_tags と同一の内容。root_block_device / aws_ec2_tag /
  # DLM の tags_to_add には default_tags が伝播しないため明示的に使い回す。
  common_tags = {
    DoNotNuke      = "true"
    SystemName     = local.project_name
    SystemCode     = "00-01-01"
    Env            = local.environment
    Owner          = "sre"
    CodeRepository = "local"
    RootModulePath = "terraform"
  }

  # "ap-northeast-1a" -> "1a"
  az_suffix = substr(var.availability_zone, length(var.availability_zone) - 2, 2)

  names = {
    vpc             = format(local.name_fmt, "vpc")
    subnet          = format(local.name_fmt, "public-${local.az_suffix}-subnet")
    igw             = format(local.name_fmt, "igw")
    public_rt       = format(local.name_fmt, "public-rt")
    default_rt      = format(local.name_fmt, "default-rt")
    default_sg      = format(local.name_fmt, "default-sg")
    default_nacl    = format(local.name_fmt, "default-nacl")
    sg              = format(local.name_fmt, "sg")
    instance        = format(local.name_fmt, "ec2")
    eni             = format(local.name_fmt, "eni")
    root_ebs        = format(local.name_fmt, "root-ebs")
    data_ebs        = format(local.name_fmt, "data-ebs")
    data_snapshot   = format(local.name_fmt, "data-snapshot")
    eip             = format(local.name_fmt, "eip")
    ec2_role        = format(local.name_fmt, "ec2-role")
    cwlogs_policy   = format(local.name_fmt, "cwlogs-policy")
    log_group       = format(local.name_fmt, "containers-cw")
    alarm           = format(local.name_fmt, "statuscheck-cw")
    deploy_bucket   = format(local.name_fmt, "deploy-s3")
    app_bundle      = format(local.name_fmt, "app-bundle")
    ssm_association = format(local.name_fmt, "app-deploy")
    dlm_role        = format(local.name_fmt, "dlm-role")
    dlm_policy      = format(local.name_fmt, "data-dlm")
    dlm_target      = format(local.name_fmt, "data")
    hostname        = "${local.project_name}-${local.environment}"
  }

  # SG ingress の description 用（ポート -> 役割）
  service_port_roles = {
    "6900" = "login"
    "6121" = "char"
    "5121" = "map"
  }

  # data EBS のマウント先とアプリ配置先（OS 内部パス）
  mount_point = "/srv/ro-server"
  app_dir     = "/srv/ro-server/app"

  # デプロイバンドル
  deploy_object_key = "app.zip"
  ssm_output_prefix = "ssm-output"
}
