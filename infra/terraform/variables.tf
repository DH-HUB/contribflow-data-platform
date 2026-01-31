variable "aws_region" { type = string, default = "eu-west-3" }
variable "s3_bucket_name" { type = string }
variable "rds_instance_class" { type = string, default = "db.t3.micro" }
variable "rds_username" { type = string, default = "warehouse" }
variable "rds_password" { type = string, sensitive = true }
