resource "aws_security_group" "app" {
  name        = local.names.sg
  description = "Application server: inbound service ports only (no SSH / no MySQL)"
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = local.names.sg
  }
}

# 22 / 3306 は開けない。IPv6 ルールも作らない。
resource "aws_vpc_security_group_ingress_rule" "app" {
  for_each = toset([for port in var.service_ports : tostring(port)])

  security_group_id = aws_security_group.app.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = tonumber(each.key)
  to_port           = tonumber(each.key)
  description       = "App service port ${each.key} (${lookup(local.service_port_roles, each.key, "service")})"

  tags = {
    Name = format(local.name_fmt, "${each.key}-sgr")
  }
}

# dnf / docker pull / SSM / S3 のアウトバウンド用
resource "aws_vpc_security_group_egress_rule" "all" {
  security_group_id = aws_security_group.app.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Allow all outbound (dnf, docker pull, SSM, S3)"

  tags = {
    Name = format(local.name_fmt, "egress-sgr")
  }
}
