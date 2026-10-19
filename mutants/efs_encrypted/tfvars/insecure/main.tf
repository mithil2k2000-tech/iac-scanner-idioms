terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {}

resource "aws_efs_file_system" "this" {
  creation_token = "app"
  encrypted      = var.setting
}
