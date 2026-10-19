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

resource "aws_kinesis_stream" "this" {
  name            = "app"
  shard_count     = 1
  encryption_type = var.production ? "NONE" : "KMS"
  kms_key_id      = "alias/aws/kinesis"
}
