variable "setting" {}

resource "aws_cloudtrail" "this" {
  name                       = "app"
  s3_bucket_name             = "app-trail"
  is_multi_region_trail      = true
  enable_log_file_validation = var.setting
}
