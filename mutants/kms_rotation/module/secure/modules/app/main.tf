variable "setting" {}

resource "aws_kms_key" "this" {
  description         = "app"
  enable_key_rotation = var.setting
}
