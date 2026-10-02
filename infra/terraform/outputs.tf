output "public_ip" { value = aws_instance.app.public_ip }
output "log_group" { value = aws_cloudwatch_log_group.application.name }
