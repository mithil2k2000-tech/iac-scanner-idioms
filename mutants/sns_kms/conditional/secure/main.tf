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

resource "aws_sns_topic" "this" {
  name              = "app"
  kms_master_key_id = var.production ? "alias/aws/sns" : null
}
