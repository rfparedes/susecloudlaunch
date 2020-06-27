## Connection, authentication, application configuration variables

# define the credentials profile
variable "aws_profile_1" {
  type = string
  description = "AWS credentials"
}

# define application name
variable "app_name_1" {
  type = string
  description = "Application name"
}

# define application environment
variable "app_environment_1" {
  type = string
  description = "Application environment"
}

# define ssh keys
variable "aws_key_pair_1" {
  type = string
  description = "Key Pair"
}
##########################################################################

## Network variables

# define region
variable "aws_region_1" {
  type = string
  description = "AWS region"
}

# define zone
variable "aws_zone_1" {
  type = string
  description = "AWS availability zone"
}

# define VPC cidr range
variable "private_vpc_cidr_1" {
  type = string
  description = "VPC CIDR range 1"
}

# define private subnet
variable "private_subnet_cidr_1" {
  type = string
  description = "private subnet CIDR 1"
}

##########################################################################

## Instance variables

# define instance type
variable "aws_instance_type_1" {
  type = string
  description = "Instance type" 
}

# define AMI
variable "aws_ami_1" {
  type = string
  description = "AMI"
}

