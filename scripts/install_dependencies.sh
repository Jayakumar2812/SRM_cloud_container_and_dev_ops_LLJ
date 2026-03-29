#!/bin/bash
set -euo pipefail

if command -v yum >/dev/null 2>&1; then
  yum update -y
  yum install -y httpd
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y httpd
else
  echo "Supported package manager not found."
  exit 1
fi

systemctl enable httpd
systemctl start httpd

mkdir -p /var/www/portfolio-app
