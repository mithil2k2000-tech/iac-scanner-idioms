variable "setting" {}

resource "aws_sns_topic" "this" {
  name              = "app"
  kms_master_key_id = var.setting
}
