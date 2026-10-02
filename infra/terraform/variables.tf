variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "openeval-demo"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "ssh_key_name" {
  type        = string
  description = "Existing EC2 key pair name"
}

variable "admin_cidr" {
  type        = string
  description = "Your public IP /32 for SSH; never use 0.0.0.0/0"
}
