variable "setting" {}

resource "aws_s3_bucket_acl" "this" {
  bucket = "app-bucket"
  acl    = var.setting
}
