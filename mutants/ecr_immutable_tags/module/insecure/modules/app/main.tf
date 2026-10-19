variable "setting" {}

resource "aws_ecr_repository" "this" {
  name                 = "app"
  image_tag_mutability = var.setting
  image_scanning_configuration {
    scan_on_push = true
  }
}
