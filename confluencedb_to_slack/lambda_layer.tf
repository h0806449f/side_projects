module "lambda_layer_local" {
  source = "terraform-aws-modules/lambda/aws"

  create_layer = true

  layer_name               = "layer_of_auto_update_sup_km"
  description              = "layer_of_auto_update_sup_km"
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  layer_skip_destroy       = false

  source_path = "${path.module}/lambda-layer"
}
