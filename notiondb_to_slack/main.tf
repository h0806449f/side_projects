# terraform 本身的 config
terraform {
  required_version = "~> 1.8"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.63"
    }
  }

  backend "s3" {
    bucket              = "gc-playground-tfstates"
    key                 = "feat/read-notion-for-SUP-KM.tfstate"
    region              = "ap-northeast-1"
    dynamodb_table      = "tf-locks"
    profile             = "tf-gc-playground"
    allowed_account_ids = ["593713876380"]
  }
}

# provider AWS 的 config
provider "aws" {
  region              = "ap-northeast-1"
  profile             = "tf-gc-playground"
  allowed_account_ids = ["593713876380"]

  default_tags {
    tags = {
      Managed = "terraform"
      Source  = "going-cloud/sup/git-playground"
    }
  }
}
