terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {
  default = true
}

resource "aws_kms_key" "this" {
  description         = "app"
  enable_key_rotation = var.setting
}
