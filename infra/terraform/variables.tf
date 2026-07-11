variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "aak-erp"
}

variable "aws_region" {
  description = "AWS region — ap-south-1 (Mumbai) is closest to Sri Lanka"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type. t3.large (2 vCPU, 8GB) recommended for ERPNext."
  type        = string
  default     = "t3.large"
}

variable "root_volume_size_gb" {
  description = "Root EBS volume size in GB"
  type        = number
  default     = 50
}

variable "s3_backup_bucket" {
  description = "S3 bucket name for automated ERPNext backups"
  type        = string
  default     = "aak-erp-backups"
}

variable "ssh_public_key" {
  description = "Your SSH public key content (e.g. contents of ~/.ssh/id_ed25519.pub)"
  type        = string
  sensitive   = true
}

variable "ssh_allowed_cidrs" {
  description = "List of CIDR blocks allowed to SSH. Restrict to your IP for production."
  type        = list(string)
  default     = ["0.0.0.0/0"] # Replace with your IP/32 before apply
}
