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

resource "aws_ecr_repository" "this" {
  name                 = "app"
  image_tag_mutability = var.production ? "IMMUTABLE" : "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}
