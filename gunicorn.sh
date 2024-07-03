#!/bin/bash

sudo mkdir /var/log/gunicorn
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status

echo "Supervisor configured"
