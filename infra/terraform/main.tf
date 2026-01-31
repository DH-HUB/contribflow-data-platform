terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "contribflow" {
  bucket = var.s3_bucket_name
}

resource "aws_db_instance" "warehouse" {
  identifier          = "contribflow-warehouse"
  engine              = "postgres"
  engine_version      = "16.1"
  instance_class      = var.rds_instance_class
  allocated_storage   = 20
  db_name             = "warehouse"
  username            = var.rds_username
  password            = var.rds_password
  skip_final_snapshot = true
  publicly_accessible = true
}
