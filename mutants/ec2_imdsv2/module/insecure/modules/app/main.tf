variable "setting" {}

resource "aws_instance" "this" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = var.setting
  }
}
