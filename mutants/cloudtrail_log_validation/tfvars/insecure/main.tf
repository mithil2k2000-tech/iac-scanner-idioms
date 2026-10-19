terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {}

resource "aws_cloudtrail" "this" {
  name                       = "app"
  s3_bucket_name             = "app-trail"
  is_multi_region_trail      = true
  enable_log_file_validation = var.setting
}
