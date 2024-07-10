#!/bin/bash
sudo cp -rf declaration-management.socket /etc/systemd/system/
sudo cp -rf declaration-management.service /etc/systemd/system/

sudo systemctl start declaration-management
sudo systemctl enable declaration-management
sudo systemctl status declaration-management

sudo systemctl restart nginx
sudo supervisorctl restart declaration_group:declaration-management
