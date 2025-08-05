# Variables for Lex Integration

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "bookings_table_name" {
  description = "Name of the DynamoDB bookings table"
  type        = string
  default     = "DALScooterBookings"
}

variable "users_table_name" {
  description = "Name of the DynamoDB users table"
  type        = string
  default     = "DALScooterUsers"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "DALScooter"
} 