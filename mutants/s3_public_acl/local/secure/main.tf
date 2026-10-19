terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = "private"
}

resource "aws_s3_bucket_acl" "this" {
  bucket = "app-bucket"
  acl    = local.setting
}
