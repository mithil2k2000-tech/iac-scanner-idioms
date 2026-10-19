terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = false
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = "app-bucket"
  block_public_acls       = local.setting
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
