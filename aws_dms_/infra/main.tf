terraform {
  required_version = "~> 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.63"
    }
  }
}

provider "aws" {
  region              = "ap-northeast-1"
  profile             = "tf-gc-playground"
  allowed_account_ids = ["593713876380"]

  default_tags {
    tags = {
      Managed = "terraform"
    }
  }
}
