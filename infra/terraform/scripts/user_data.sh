#!/bin/bash
# Bootstrap script for AAK ERP server (Ubuntu 22.04)
# Runs once on first boot via EC2 user_data.
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
PROJECT="${project_name}"
AWS_REGION="${aws_region}"
S3_BUCKET="${s3_bucket}"

echo "=== [AAK ERP] Bootstrap started ==="

# ── System updates ─────────────────────────────────────────────────────────────
apt-get update -y
apt-get upgrade -y
apt-get install -y \
  ca-certificates curl gnupg lsb-release \
  git unzip awscli fail2ban ufw

# ── Docker ─────────────────────────────────────────────────────────────────────
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# ── Firewall (UFW) ─────────────────────────────────────────────────────────────
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# ── Fail2ban ───────────────────────────────────────────────────────────────────
systemctl enable fail2ban
systemctl start fail2ban

# ── Clone the repo ─────────────────────────────────────────────────────────────
mkdir -p /opt/aak-erp
git clone https://github.com/lakal96/aak-erp.git /opt/aak-erp
chown -R ubuntu:ubuntu /opt/aak-erp

# ── AWS Region for CLI ─────────────────────────────────────────────────────────
aws configure set region "$AWS_REGION"

echo "=== [AAK ERP] Bootstrap complete ==="
echo "Next steps:"
echo "  1. SSH to the server: ssh ubuntu@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "  2. cd /opt/aak-erp"
echo "  3. cp .env.production.example .env && edit .env"
echo "  4. Run: docker compose -f compose.yaml -f overrides/compose.mariadb.yaml \\"
echo "            -f overrides/compose.redis.yaml -f overrides/compose.traefik-ssl.yaml \\"
echo "            -f overrides/compose.aak-production.yaml up -d"
