# setup the AWS provider | provider.tf
terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  profile     = var.aws_profile_1
  region      = var.aws_region_1
}
