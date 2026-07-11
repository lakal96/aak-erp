output "server_public_ip" {
  description = "Static public IP of the ERP server (point your domain A record here)"
  value       = aws_eip.erp.public_ip
}

output "server_public_dns" {
  description = "Public DNS hostname of the ERP server"
  value       = aws_instance.erp.public_dns
}

output "s3_bucket_name" {
  description = "S3 backup bucket name"
  value       = aws_s3_bucket.backups.id
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.erp.id
}

output "ssh_command" {
  description = "SSH command to connect to the server"
  value       = "ssh ubuntu@${aws_eip.erp.public_ip}"
}
