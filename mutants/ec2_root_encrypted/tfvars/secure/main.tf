terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {}

resource "aws_instance" "this" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  root_block_device {
    encrypted = var.setting
  }
}
