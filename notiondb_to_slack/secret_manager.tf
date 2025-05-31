# secret manager
# note : secret manager name 不可以與正在刪除階段的 secret 同名
# note : 名字後加上 mmdd-n 次數
resource "aws_secretsmanager_secret" "henry_testtf_lambda_secret_v240627" {
  name       = "henry_testtf_lambda_secret_v240627"
  kms_key_id = aws_kms_key.henry_testtf_lambda_kmskey.key_id

  tags = {
    "Retention" = "2025-12-31"
  }
}

# secret manager's key_value_pair
resource "aws_secretsmanager_secret_version" "henry_testtf_lambda_secret_version" {
  secret_id     = aws_secretsmanager_secret.henry_testtf_lambda_secret_v240627.id
  secret_string = jsonencode(var.henry_secret)
}

# KMS key for secret manager
resource "aws_kms_key" "henry_testtf_lambda_kmskey" {
  description         = "this is kms key for SUP KM read notion"
  enable_key_rotation = true

  tags = {
    "Retention" = "2025-12-31"
  }
}
