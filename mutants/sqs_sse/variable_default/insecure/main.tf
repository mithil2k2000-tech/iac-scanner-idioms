terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {
  default = false
}

resource "aws_sqs_queue" "this" {
  name                    = "app"
  sqs_managed_sse_enabled = var.setting
}
