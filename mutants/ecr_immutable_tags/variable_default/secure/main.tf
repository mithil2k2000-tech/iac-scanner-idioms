terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

variable "setting" {
  default = "IMMUTABLE"
}

resource "aws_ecr_repository" "this" {
  name                 = "app"
  image_tag_mutability = var.setting
  image_scanning_configuration {
    scan_on_push = true
  }
}
