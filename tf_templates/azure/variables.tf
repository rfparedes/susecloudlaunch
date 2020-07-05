## Connection, authentication, application configuration variables

# define application name
variable "app_name_1" {
  type        = string
  description = "Application name"
}

# define ssh keys
variable "azure_key_pair_1" {
  type        = string
  description = "Key Pair"
}
##########################################################################

## Network variables

# define region
variable "azure_region_1" {
  type        = string
  description = "Azure region"
}

# define VPC cidr range
variable "private_vpc_cidr_1" {
  type        = string
  description = "VPC CIDR range 1"
}

# define private subnet
variable "private_subnet_cidr_1" {
  type        = string
  description = "private subnet CIDR 1"
}

##########################################################################

## Instance variables

# define instance type
variable "azure_instance_type_1" {
  type        = string
  description = "Instance type"
}

# define Image reference
variable "azure_image_offer" {
  type        = string
  description = "image offer"
}
variable "azure_image_sku" {
  type        = string
  description = "image sku"
}
variable "azure_image_version" {
  type        = string
  description = "image version"
}

