variable "setting" {}

resource "aws_security_group" "this" {
  name        = "app"
  description = "app servers"
  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.setting
  }
}
