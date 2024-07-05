#!/bin/bash
sudo cp -rf declaration-management.conf /etc/supervisor/conf.d/
sudo mkdir /var/log/gunicorn
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

echo "Supervisor configured"
