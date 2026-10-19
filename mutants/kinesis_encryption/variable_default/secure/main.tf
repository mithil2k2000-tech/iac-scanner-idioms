terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {
  default = "KMS"
}

resource "aws_kinesis_stream" "this" {
  name            = "app"
  shard_count     = 1
  encryption_type = var.setting
  kms_key_id      = "alias/aws/kinesis"
}
