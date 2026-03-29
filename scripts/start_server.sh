#!/bin/bash
set -euo pipefail

mkdir -p /var/www/html
rm -rf /var/www/html/*
cp -R /var/www/portfolio-app/* /var/www/html/

chown -R apache:apache /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;

systemctl restart httpd
