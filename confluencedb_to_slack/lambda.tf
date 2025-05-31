# module link: https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest

# lambda for update sup km database
data "archive_file" "auto_update_sup_km" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_sup_km"
  output_path = "${path.module}/lambda_sup_km/lambda_functional_code.zip"
}

module "auto_update_sup_km" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "auto_update_sup_km"
  description   = "This lambda will post oldest SUP KM article to slack channel(#going-cloud-cloud-support)"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"
  timeout       = 240

  create_package         = false
  local_existing_package = data.archive_file.auto_update_sup_km.output_path

  layers = [
    module.lambda_layer_local.lambda_layer_arn
  ]

  environment_variables = {
    CONFLUENCE_API_TOKEN = var.confluence_api_token
    SLACK_WEBHOOK        = var.slack_webhook
  }

  attach_policy_json = true
  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Decrypt"]
        Resource = "*"
      }
    ]
  })
}


# lambda for update aws km database
data "archive_file" "auto_update_aws_km" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_aws_km"
  output_path = "${path.module}/lambda_aws_km/lambda_functional_code.zip"
}

module "auto_update_aws_km" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "auto_update_aws_km"
  description   = "This lambda will post oldest AWS KM article to slack channel(#going-cloud-cloud-support)"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"
  timeout       = 240

  create_package         = false
  local_existing_package = data.archive_file.auto_update_aws_km.output_path

  layers = [
    module.lambda_layer_local.lambda_layer_arn
  ]

  environment_variables = {
    CONFLUENCE_API_TOKEN = var.confluence_api_token
    SLACK_WEBHOOK        = var.slack_webhook
  }

  attach_policy_json = true
  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:*"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["kms:Decrypt"]
        Resource = "*"
      }
    ]
  })
}
