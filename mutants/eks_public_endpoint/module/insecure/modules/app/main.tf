variable "setting" {}

resource "aws_eks_cluster" "this" {
  name     = "app"
  role_arn = "arn:aws:iam::123456789012:role/eks"
  vpc_config {
    subnet_ids              = ["subnet-1", "subnet-2"]
    endpoint_private_access = true
    endpoint_public_access  = var.setting
  }
}
