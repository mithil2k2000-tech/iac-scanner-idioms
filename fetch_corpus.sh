#!/usr/bin/env bash
# Clone the real-world corpus and Semgrep's rules (shallow clones of the default branch).
set -u
cd "$(dirname "$0")"
git clone -q --depth 1 https://github.com/semgrep/semgrep-rules.git semgrep-rules
mkdir -p corpus
for m in vpc s3-bucket rds rds-aurora eks ec2-instance security-group iam lambda alb autoscaling cloudfront dynamodb-table kms sqs sns \
  ecs elasticache efs redshift msk-kafka-cluster apigateway-v2 acm route53 cloudwatch step-functions eventbridge opensearch \
  secrets-manager ssm-parameter batch vpn-gateway transit-gateway appsync dms emr fsx global-accelerator memory-db network-firewall \
  key-pair ecr elb atlantis notify-slack customer-gateway s3-object rds-proxy app-runner managed-service-prometheus \
  managed-service-grafana datadog-forwarders; do
  git clone -q --depth 1 "https://github.com/terraform-aws-modules/terraform-aws-$m.git" "corpus/aws-$m" || echo "missing $m"
done
git clone -q --depth 1 https://github.com/bridgecrewio/terragoat.git corpus/terragoat
