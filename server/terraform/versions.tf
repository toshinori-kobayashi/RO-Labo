terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.7"
    }
  }

  # state はローカル保持（Sandbox の aws-nuke が S3Object を毎晩削除するため S3 backend は使わない）
}
