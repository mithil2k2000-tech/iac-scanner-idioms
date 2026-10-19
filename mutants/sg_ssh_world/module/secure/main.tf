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
  setting = ["10.0.0.0/8"]
}
