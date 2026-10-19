terraform {
  required_providers {
    aws = { source = "hashicorp/aws" }
  }
}

provider "aws" {
  region = "eu-west-2"
}

module "app" {
  source  = "./modules/app"
  setting = null
}
