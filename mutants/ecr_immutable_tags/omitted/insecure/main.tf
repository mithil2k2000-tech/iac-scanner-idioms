terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

resource "aws_ecr_repository" "this" {
  name                 = "app"
  image_scanning_configuration {
    scan_on_push = true
  }
}
