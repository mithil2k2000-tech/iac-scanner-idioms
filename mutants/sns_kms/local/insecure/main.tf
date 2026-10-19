terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = null
}

resource "aws_sns_topic" "this" {
  name              = "app"
  kms_master_key_id = local.setting
}
