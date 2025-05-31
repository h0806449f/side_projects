## IAM role for event bridge
##
resource "aws_iam_role" "this" {
  name               = "role_for_auto_update_sup_km"
  assume_role_policy = data.aws_iam_policy_document.this.json
}


## trusted polict for IAM role
##
data "aws_iam_policy_document" "this" {
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
resource "aws_iam_role_policy" "this" {
  name = "policy_for_auto_update_sup_km"
  role = aws_iam_role.this.id
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
resource "aws_scheduler_schedule" "sup_km" {
  name       = "scheduler_for_auto_update_sup_km"
  group_name = "default"
  flexible_time_window {
    mode = "OFF"
  }
  # schedule_expression          = "cron(30 9 ? * MON-FRI *)"
  schedule_expression          = "cron(30 9 ? * 2 *)"
  schedule_expression_timezone = "Asia/Taipei"
  target {
    arn      = module.auto_update_sup_km.lambda_function_arn
    role_arn = aws_iam_role.this.arn
  }
}

resource "aws_scheduler_schedule" "aws_km" {
  name       = "scheduler_for_auto_update_aws_km"
  group_name = "default"
  flexible_time_window {
    mode = "OFF"
  }
  schedule_expression          = "cron(30 9 ? * MON-FRI *)"
  schedule_expression_timezone = "Asia/Taipei"
  target {
    arn      = module.auto_update_aws_km.lambda_function_arn
    role_arn = aws_iam_role.this.arn
  }
}
