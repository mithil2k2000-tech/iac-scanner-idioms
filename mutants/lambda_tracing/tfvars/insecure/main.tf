terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {}

resource "aws_lambda_function" "this" {
  function_name = "app"
  role          = "arn:aws:iam::123456789012:role/app"
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "app.zip"
  tracing_config {
    mode = var.setting
  }
}
