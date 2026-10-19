variable "setting" {}

resource "aws_efs_file_system" "this" {
  creation_token = "app"
  encrypted      = var.setting
}
