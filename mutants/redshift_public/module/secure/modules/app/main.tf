variable "setting" {}

resource "aws_redshift_cluster" "this" {
  cluster_identifier  = "app"
  node_type           = "ra3.xlplus"
  master_username     = "app"
  manage_master_password = true
  encrypted           = true
  publicly_accessible = var.setting
}
