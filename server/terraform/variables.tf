variable "region" {
  description = "リソースを作成する AWS リージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "profile" {
  description = "使用する AWS CLI プロファイル（SSO）"
  type        = string
  default     = "sandbox-power"
}

variable "project_name" {
  description = "リソース名の先頭に付けるプロジェクト名"
  type        = string
  default     = "legacy-app-lab"
}

variable "environment" {
  description = "リソース名の末尾に付ける環境識別子"
  type        = string
  default     = "verify"
}

variable "vpc_cidr" {
  description = "VPC の CIDR ブロック"
  type        = string
  default     = "10.90.0.0/16"
}

variable "subnet_cidr" {
  description = "Public Subnet の CIDR ブロック"
  type        = string
  default     = "10.90.0.0/24"
}

variable "availability_zone" {
  description = "Subnet / EBS を配置する AZ"
  type        = string
  default     = "ap-northeast-1a"
}

variable "instance_type" {
  description = "アプリケーションサーバの EC2 インスタンスタイプ"
  type        = string
  default     = "t3.medium"
}

variable "root_volume_size_gb" {
  description = "root EBS のサイズ（GiB）"
  type        = number
  default     = 30
}

variable "data_volume_size_gb" {
  description = "data EBS のサイズ（GiB）"
  type        = number
  default     = 20
}

variable "service_ports" {
  description = "インターネットへ公開する TCP ポート（6900=login / 6121=char / 5121=map）"
  type        = list(number)
  default     = [6900, 6121, 5121]
}

variable "log_retention_days" {
  description = "CloudWatch Logs の保持日数"
  type        = number
  default     = 14
}

variable "docker_compose_version" {
  description = "user-data で導入する Docker Compose plugin のバージョン（GitHub Releases のタグ）"
  type        = string
  default     = "v5.5.1"
}

variable "docker_buildx_version" {
  description = "user-data で導入する Docker Buildx plugin のバージョン（GitHub Releases のタグ）。Compose v5 は buildx >= 0.17 を要求し、AL2023 同梱の 0.12 では build できない"
  type        = string
  default     = "v0.37.1"
}

variable "snapshot_retain_count" {
  description = "DLM が保持する data EBS スナップショットの世代数"
  type        = number
  default     = 7
}

variable "snapshot_time_utc" {
  description = "DLM スナップショットの開始時刻（UTC / HH:MM）。19:30 UTC = 04:30 JST"
  type        = string
  default     = "19:30"
}
