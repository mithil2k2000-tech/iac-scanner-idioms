variable "setting" {}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "app"
  description                = "app cache"
  node_type                  = "cache.t3.micro"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = var.setting
}
