## IAM role for event bridge
##
resource "aws_iam_role" "henry_testtf_lambda_role_for_eventbridge" {
  name               = "henry_testtf_lambda_role_for_eventbridge"
  assume_role_policy = data.aws_iam_policy_document.henry_testtf_lambda_trusted_policy_for_eventbridge.json

  tags = {
    "Retention" = "2025-12-31"
  }
}


## trusted polict for IAM role
##
data "aws_iam_policy_document" "henry_testtf_lambda_trusted_policy_for_eventbridge" {
  statement {
    sid     = "LetEventbridgeAssumeRole"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}


## permission policy for IAM role
## 
resource "aws_iam_role_policy" "henry_testtf_lambda_rolepolicy_for_eventbridge" {
  name = "henry_testtf_lambda_rolepolicy_for_eventbridge"
  role = aws_iam_role.henry_testtf_lambda_role_for_eventbridge.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["lambda:InvokeFunction"]
        Resource = "*"
      }
    ]
  })
}


## event bridge  
## 
resource "aws_scheduler_schedule" "henry_testtf_lambda_eventbridge" {
  name       = "henry_testtf_lambda_eventbridge"
  group_name = "default"
  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression          = "cron(30 9 ? * MON-FRI *)"
  schedule_expression_timezone = "Asia/Taipei"
  target {
    arn      = "arn:aws:lambda:ap-northeast-1:593713876380:function:henry-updated-SUP-KM-automation-v240607"
    role_arn = aws_iam_role.henry_testtf_lambda_role_for_eventbridge.arn
  }
}
