#!/bin/bash

echo "Updating files from development directory to production..."

# Stop services
echo "Stopping services..."
sudo systemctl stop instancemanager.service
sudo systemctl stop converter.service

# Update instancemanager files
echo "Updating instancemanager files..."
cd ~/reproduced/StreamK3s
sudo cp -r instancemanager/* /opt/Stream-Processing/instancemanager/

echo "Updating converter files..."
sudo cp -r converter_streams/* /opt/Stream-Processing/converter_streams/

echo "Updating service files..."
cd ~/reproduced/StreamK3s/installation
sudo cp instancemanager.service /etc/systemd/system/
sudo cp converter.service /etc/systemd/system/

sudo systemctl daemon-reload

echo "Starting services..."
sudo systemctl start instancemanager.service
sudo systemctl start converter.service

echo "Checking service status..."
sudo systemctl status instancemanager.service --no-pager
sudo systemctl status converter.service --no-pager

echo "Update complete!"