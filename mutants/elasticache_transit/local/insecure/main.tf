terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

locals {
  setting = false
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "app"
  description                = "app cache"
  node_type                  = "cache.t3.micro"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = local.setting
}
