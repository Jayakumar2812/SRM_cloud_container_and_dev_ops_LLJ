#!/bin/bash
set -euo pipefail

systemctl is-active --quiet httpd
test -f /var/www/html/index.html
curl -I http://localhost | grep "200 OK"
