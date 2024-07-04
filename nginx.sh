#!/bin/bash
sudo cp -rf declaration-management.socket /etc/systemd/system/
sudo cp -rf declaration-management.service /etc/systemd/system/

sudo systemctl start declaration-management.socket
sudo systemctl enable declaration-management.socket
sudo systemctl status wdeclaration-management.socket

sudo systemctl restart nginx
