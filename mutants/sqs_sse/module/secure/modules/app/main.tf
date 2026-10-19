variable "setting" {}

resource "aws_sqs_queue" "this" {
  name                    = "app"
  sqs_managed_sse_enabled = var.setting
}
