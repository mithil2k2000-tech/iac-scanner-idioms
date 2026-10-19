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

resource "aws_kms_key" "this" {
  description         = "app"
  enable_key_rotation = var.production ? true : false
}
