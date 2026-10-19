terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

resource "aws_opensearch_domain" "this" {
  domain_name = "app"
  encrypt_at_rest {
    enabled = true
  }
  node_to_node_encryption {
  }
}
