terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = true
}

resource "aws_db_instance" "this" {
  identifier          = "app"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "app"
  manage_master_user_password = true
  storage_encrypted   = true
  iam_database_authentication_enabled = local.setting
}
