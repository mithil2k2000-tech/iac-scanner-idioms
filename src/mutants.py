"""Generate the mutation corpus: one security setting, secure or insecure, written in different Terraform idioms.

Each category is one resource with one security-relevant setting. The setting's value is a plain HCL expression,
so it can be placed directly, behind a variable, a local, a conditional, a tfvars file or a local child module.
Ground truth is known by construction: the insecure value should be flagged, the secure value should not.

Layout: mutants/<category>/<idiom>/<secure|insecure>/main.tf (plus modules/ and terraform.tfvars where needed).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "mutants"

# name: (resource type, resource body with {V} where the setting goes, secure value, insecure value,
#        insecure-when-omitted, family, extra top-level HCL)
CATEGORIES: dict[str, tuple] = {
    "rds_storage_encrypted": ("aws_db_instance", '''
  identifier          = "app"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "app"
  manage_master_user_password = true
  storage_encrypted   = {V}''', "true", "false", True, "encryption at rest", ""),
    "rds_publicly_accessible": ("aws_db_instance", '''
  identifier          = "app"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "app"
  manage_master_user_password = true
  storage_encrypted   = true
  publicly_accessible = {V}''', "false", "true", False, "network exposure", ""),
    "rds_iam_auth": ("aws_db_instance", '''
  identifier          = "app"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "app"
  manage_master_user_password = true
  storage_encrypted   = true
  iam_database_authentication_enabled = {V}''', "true", "false", True, "identity", ""),
    "rds_deletion_protection": ("aws_db_instance", '''
  identifier          = "app"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "app"
  manage_master_user_password = true
  storage_encrypted   = true
  deletion_protection = {V}''', "true", "false", True, "resilience", ""),
    "ebs_volume_encrypted": ("aws_ebs_volume", '''
  availability_zone = "eu-west-2a"
  size              = 20
  encrypted         = {V}''', "true", "false", True, "encryption at rest", ""),
    "efs_encrypted": ("aws_efs_file_system", '''
  creation_token = "app"
  encrypted      = {V}''', "true", "false", True, "encryption at rest", ""),
    "sg_ssh_world": ("aws_security_group", '''
  name        = "app"
  description = "app servers"
  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = {V}
  }''', '["10.0.0.0/8"]', '["0.0.0.0/0"]', False, "network exposure", ""),
    # Since 2022 new SQS queues get SSE-SQS by default, so omitting the setting is secure.
    "sqs_sse": ("aws_sqs_queue", '''
  name                    = "app"
  sqs_managed_sse_enabled = {V}''', "true", "false", False, "encryption at rest", ""),
    "sns_kms": ("aws_sns_topic", '''
  name              = "app"
  kms_master_key_id = {V}''', '"alias/aws/sns"', "null", True, "encryption at rest", ""),
    "kms_rotation": ("aws_kms_key", '''
  description         = "app"
  enable_key_rotation = {V}''', "true", "false", True, "key management", ""),
    "dynamodb_pitr": ("aws_dynamodb_table", '''
  name         = "app"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "S"
  }
  point_in_time_recovery {
    enabled = {V}
  }''', "true", "false", True, "resilience", ""),
    "cloudtrail_log_validation": ("aws_cloudtrail", '''
  name                       = "app"
  s3_bucket_name             = "app-trail"
  is_multi_region_trail      = true
  enable_log_file_validation = {V}''', "true", "false", True, "logging", ""),
    "ec2_imdsv2": ("aws_instance", '''
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = {V}
  }''', '"required"', '"optional"', True, "instance hardening", ""),
    "ec2_root_encrypted": ("aws_instance", '''
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  root_block_device {
    encrypted = {V}
  }''', "true", "false", True, "encryption at rest", ""),
    "lambda_tracing": ("aws_lambda_function", '''
  function_name = "app"
  role          = "arn:aws:iam::123456789012:role/app"
  handler       = "index.handler"
  runtime       = "python3.12"
  filename      = "app.zip"
  tracing_config {
    mode = {V}
  }''', '"Active"', '"PassThrough"', True, "logging", ""),
    "elasticache_transit": ("aws_elasticache_replication_group", '''
  replication_group_id       = "app"
  description                = "app cache"
  node_type                  = "cache.t3.micro"
  at_rest_encryption_enabled = true
  transit_encryption_enabled = {V}''', "true", "false", True, "encryption in transit", ""),
    "redshift_public": ("aws_redshift_cluster", '''
  cluster_identifier  = "app"
  node_type           = "ra3.xlplus"
  master_username     = "app"
  manage_master_password = true
  encrypted           = true
  publicly_accessible = {V}''', "false", "true", False, "network exposure", ""),
    "ecr_scan_on_push": ("aws_ecr_repository", '''
  name                 = "app"
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = {V}
  }''', "true", "false", True, "supply chain", ""),
    "ecr_immutable_tags": ("aws_ecr_repository", '''
  name                 = "app"
  image_tag_mutability = {V}
  image_scanning_configuration {
    scan_on_push = true
  }''', '"IMMUTABLE"', '"MUTABLE"', True, "supply chain", ""),
    "s3_public_acl": ("aws_s3_bucket_acl", '''
  bucket = "app-bucket"
  acl    = {V}''', '"private"', '"public-read"', False, "network exposure", ""),
    "s3_block_public_acls": ("aws_s3_bucket_public_access_block", '''
  bucket                  = "app-bucket"
  block_public_acls       = {V}
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true''', "true", "false", True, "network exposure", ""),
    "kinesis_encryption": ("aws_kinesis_stream", '''
  name            = "app"
  shard_count     = 1
  encryption_type = {V}
  kms_key_id      = "alias/aws/kinesis"''', '"KMS"', '"NONE"', True, "encryption at rest", ""),
    "opensearch_node_to_node": ("aws_opensearch_domain", '''
  domain_name = "app"
  encrypt_at_rest {
    enabled = true
  }
  node_to_node_encryption {
    enabled = {V}
  }''', "true", "false", True, "encryption in transit", ""),
    "eks_public_endpoint": ("aws_eks_cluster", '''
  name     = "app"
  role_arn = "arn:aws:iam::123456789012:role/eks"
  vpc_config {
    subnet_ids              = ["subnet-1", "subnet-2"]
    endpoint_private_access = true
    endpoint_public_access  = {V}
  }''', "false", "true", True, "network exposure", ""),
}

PROVIDER = 'terraform {\n  required_providers {\n    aws = { source = "hashicorp/aws" }\n  }\n}\n\nprovider "aws" {\n  region = "eu-west-2"\n}\n'
IDIOMS = ["literal", "variable_default", "tfvars", "local", "conditional", "module", "omitted"]


def resource(rtype: str, body: str, expr: str | None) -> str:
    if expr is None:  # drop the line (or block line) that holds the setting
        body = "\n".join(line for line in body.splitlines() if "{V}" not in line)
    else:
        body = body.replace("{V}", expr)
    return f'resource "{rtype}" "this" {{{body}\n}}\n'


def write_case(path: Path, idiom: str, rtype: str, body: str, value: str, other: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    if idiom == "literal":
        files["main.tf"] = PROVIDER + "\n" + resource(rtype, body, value)
    elif idiom == "omitted":
        files["main.tf"] = PROVIDER + "\n" + resource(rtype, body, None)
    elif idiom == "variable_default":
        files["main.tf"] = PROVIDER + f'\nvariable "setting" {{\n  default = {value}\n}}\n\n' + resource(rtype, body, "var.setting")
    elif idiom == "tfvars":
        files["main.tf"] = PROVIDER + '\nvariable "setting" {}\n\n' + resource(rtype, body, "var.setting")
        files["terraform.tfvars"] = f"setting = {value}\n"
    elif idiom == "local":
        files["main.tf"] = PROVIDER + f"\nlocals {{\n  setting = {value}\n}}\n\n" + resource(rtype, body, "local.setting")
    elif idiom == "conditional":
        # A feature flag selects the value; the flag's default picks `value`.
        files["main.tf"] = (PROVIDER + '\nvariable "production" {\n  default = true\n}\n\n'
                            + resource(rtype, body, f"var.production ? {value} : {other}"))
    elif idiom == "module":
        files["main.tf"] = PROVIDER + f'\nmodule "app" {{\n  source  = "./modules/app"\n  setting = {value}\n}}\n'
        files["modules/app/main.tf"] = 'variable "setting" {}\n\n' + resource(rtype, body, "var.setting")
    for name, text in files.items():
        f = path / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)


def main() -> None:
    shutil.rmtree(OUT, ignore_errors=True)
    meta = []
    for cat, (rtype, body, secure, insecure, omit_insecure, family, _extra) in CATEGORIES.items():
        for idiom in IDIOMS:
            for label, value, other in (("secure", secure, insecure), ("insecure", insecure, secure)):
                if idiom == "omitted":
                    # Omission is one case whose ground truth is the provider default.
                    if label == "secure":
                        continue
                    truth = "insecure" if omit_insecure else "secure"
                    write_case(OUT / cat / idiom / truth, idiom, rtype, body, value, other)
                    meta.append({"category": cat, "family": family, "idiom": idiom, "truth": truth, "resource": rtype})
                    continue
                write_case(OUT / cat / idiom / label, idiom, rtype, body, value, other)
                meta.append({"category": cat, "family": family, "idiom": idiom, "truth": label, "resource": rtype})
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "mutants.json").write_text(json.dumps(meta, indent=1))
    print(len(meta), "cases in", len(CATEGORIES), "categories")


if __name__ == "__main__":
    main()
