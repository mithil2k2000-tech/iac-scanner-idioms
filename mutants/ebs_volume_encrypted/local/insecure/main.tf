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

resource "aws_ebs_volume" "this" {
  availability_zone = "eu-west-2a"
  size              = 20
  encrypted         = local.setting
}
