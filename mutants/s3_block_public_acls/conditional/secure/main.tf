terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "production" {
  default = true
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = "app-bucket"
  block_public_acls       = var.production ? true : false
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
