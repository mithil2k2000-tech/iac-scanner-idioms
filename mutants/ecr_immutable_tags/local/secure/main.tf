terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = "IMMUTABLE"
}

resource "aws_ecr_repository" "this" {
  name                 = "app"
  image_tag_mutability = local.setting
  image_scanning_configuration {
    scan_on_push = true
  }
}
