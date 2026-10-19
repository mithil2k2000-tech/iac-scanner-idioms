terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = ["0.0.0.0/0"]
}

resource "aws_security_group" "this" {
  name        = "app"
  description = "app servers"
  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = local.setting
  }
}
