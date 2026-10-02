# AWS deployment template

This is an EC2 demonstration template, not a record of an actual deployment. It creates an encrypted EC2 volume, limited security group, instance role for one CloudWatch log group, and a 14 day log group. PostgreSQL and Redis remain local Compose services. The default VPC is required.

1. Own a DNS name and point its A record to the instance IP. Caddy obtains an HTTPS certificate on first start.
2. Install Terraform and AWS CLI with credentials for your own account. Review `terraform plan` and costs. From `infra/terraform`, set `ssh_key_name` and `admin_cidr` in `terraform.tfvars`, then run `terraform init` and `terraform apply`.
3. Copy this repository to `/opt/openeval` on the instance over SSH using your existing key. Create `/opt/openeval/.env` with unique `API_TOKEN`, `POSTGRES_PASSWORD`, `DOMAIN`, `AWS_REGION`, and `AWS_LOG_GROUP` from Terraform output. Restrict permissions with `chmod 600 .env`.
4. From `/opt/openeval`, run `docker compose --env-file .env -f infra/docker/compose.yml -f infra/aws/compose.aws.yml up --build -d --wait`.
5. Check `https://YOUR_DOMAIN`, `https://YOUR_DOMAIN/api/health`, and CloudWatch log streams. Record task IDs from the UI and trace them in the worker log and `/tasks/{id}/events`.
6. For rollback, checkout the previous known good commit and recreate services. Back up PostgreSQL before any schema change. Stop the EC2 instance or run `terraform destroy` when done to stop charges.

The Compose override uses the YAML `!reset` tag supported by recent Docker Compose. Confirm with `docker compose version` and `docker compose ... config` before deployment. IAM grants only CloudWatch log stream write access; S3 upload and Athena are outside this stack and need separate scoped permissions. This template does not provide automated backups, secret rotation, multi AZ availability, or a managed database.
