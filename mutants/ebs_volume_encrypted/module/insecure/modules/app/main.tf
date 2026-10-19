variable "setting" {}

resource "aws_ebs_volume" "this" {
  availability_zone = "eu-west-2a"
  size              = 20
  encrypted         = var.setting
}
