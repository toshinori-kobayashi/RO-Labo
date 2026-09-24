# データ用 EBS。インスタンスを作り直してもデータを残すため独立管理。
resource "aws_ebs_volume" "data" {
  availability_zone = aws_subnet.public.availability_zone
  size              = var.data_volume_size_gb
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = local.names.data_ebs

    # DLM のターゲット判定に使う
    DlmBackup = local.names.dlm_target
  }
}

resource "aws_instance" "app" {
  ami                    = data.aws_ssm_parameter.al2023.value
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  ebs_optimized           = true
  monitoring              = false
  disable_api_termination = false

  # t3 は新規起動時のクレジット残高がゼロのため、standard だと初回の rAthena ビルドが
  # ベースライン 20% に張り付いて数倍遅くなる。unlimited（t3 の既定）にしてビルドを
  # 素直に走らせる。サープラス課金は $0.05/vCPU 時で、ビルド 1 回あたり数セント。
  credit_specification {
    cpu_credits = "unlimited"
  }

  # IMDSv2 必須。hop limit 1 でコンテナから IMDS に到達させない。
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size_gb
    encrypted             = true
    delete_on_termination = true

    # default_tags は root_block_device に伝播しないので明示的に付与
    tags = merge(local.common_tags, {
      Name = local.names.root_ebs
    })
  }

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    data_volume_id         = aws_ebs_volume.data.id
    mount_point            = local.mount_point
    docker_compose_version = var.docker_compose_version
    docker_buildx_version  = var.docker_buildx_version
    region                 = var.region
    hostname               = local.names.hostname
  })
  user_data_replace_on_change = true

  tags = {
    Name = local.names.instance
  }

  # AMI の更新でインスタンスが作り直されないようにする
  lifecycle {
    ignore_changes = [ami]
  }
}

resource "aws_volume_attachment" "data" {
  device_name                    = "/dev/sdf"
  volume_id                      = aws_ebs_volume.data.id
  instance_id                    = aws_instance.app.id
  stop_instance_before_detaching = true
}

resource "aws_eip" "app" {
  domain = "vpc"

  tags = {
    Name = local.names.eip
  }

  depends_on = [aws_internet_gateway.main]
}

resource "aws_eip_association" "app" {
  allocation_id = aws_eip.app.id
  instance_id   = aws_instance.app.id
}

# default_tags は aws_ec2_tag に適用されないため、ENI には個別にタグを付ける
resource "aws_ec2_tag" "primary_eni" {
  for_each = merge(local.common_tags, {
    Name = local.names.eni
  })

  resource_id = aws_instance.app.primary_network_interface_id
  key         = each.key
  value       = each.value
}
