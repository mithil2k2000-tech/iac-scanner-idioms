variable "setting" {}

resource "aws_opensearch_domain" "this" {
  domain_name = "app"
  encrypt_at_rest {
    enabled = true
  }
  node_to_node_encryption {
    enabled = var.setting
  }
}
