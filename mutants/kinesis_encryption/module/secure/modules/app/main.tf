variable "setting" {}

resource "aws_kinesis_stream" "this" {
  name            = "app"
  shard_count     = 1
  encryption_type = var.setting
  kms_key_id      = "alias/aws/kinesis"
}
