data "archive_file" "lambda_functional_code" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda/lambda_functional_code.zip"
}

module "lambda_function_existing_package_local" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "henry-updated-SUP-KM-automation-v240607"
  description   = "Update SUP KM database and send to SUP slack"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"
  timeout       = 180

  create_package         = false
  local_existing_package = data.archive_file.lambda_functional_code.output_path

  layers = [
    module.lambda_layer_local.lambda_layer_arn
  ]

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

  tags = {
    "Retention" = "2025-12-31"
  }
}
