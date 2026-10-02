#!/bin/bash
set -euxo pipefail
apt-get update
apt-get install -y ca-certificates curl git docker.io docker-compose-v2
systemctl enable --now docker
usermod -aG docker ubuntu
