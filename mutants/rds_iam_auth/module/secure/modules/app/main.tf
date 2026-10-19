variable "setting" {}

resource "aws_db_instance" "this" {
  identifier          = "app"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "app"
  manage_master_user_password = true
  storage_encrypted   = true
  iam_database_authentication_enabled = var.setting
}
