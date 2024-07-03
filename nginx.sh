#!/bin/bash
sudo cp -rf warehouse_management.socket /etc/systemd/system/
sudo cp -rf warehouse_management.service /etc/systemd/system/

sudo systemctl start warehouse_management.socket
sudo systemctl enable warehouse_management.socket
sudo systemctl status warehouse_management.socket

sudo systemctl restart nginx
