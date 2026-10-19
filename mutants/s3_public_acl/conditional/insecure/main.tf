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

resource "aws_s3_bucket_acl" "this" {
  bucket = "app-bucket"
  acl    = var.production ? "public-read" : "private"
}
