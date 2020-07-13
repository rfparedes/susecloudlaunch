## Connection, authentication, application configuration variables

# define GCP project name
variable "gcp_project_1" {
  type        = string
  description = "GCP Project name 1"
}

# define GCP environment name
variable "gcp_env_1" {
  type        = string
  description = "GCP env name 1"
}

# define ssh keys
variable "ssh_keys" {
  type        = string
  description = "SSH key"
}

# define machine type
variable "gcp_machine_type_1" {
  type        = string
  description = "Machine type 1"
}

# define image
variable "gcp_image_1" {
  type        = string
  description = "GCP Image 1"
}
##########################################################################

## Network variables

# define GCP region
variable "gcp_region_1" {
  type        = string
  description = "GCP region"
}

# define GCP zone
variable "gcp_zone_1" {
  type        = string
  description = "GCP zone"
}

# define private subnet
variable "private_subnet_cidr_1" {
  type        = string
  description = "private subnet CIDR 1"
}


