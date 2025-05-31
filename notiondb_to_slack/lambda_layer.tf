# side-package: pip install notion-database


module "lambda_layer_local" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name               = "henry-testlayer-SUP-KM-automation"
  description              = "Updated lambda layer for SUP KM automation"
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  layer_skip_destroy       = false


  source_path = "${path.module}/lambda-layer"

  tags = {
    "Retention" = "2025-12-31"
  }
}
