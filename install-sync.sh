#!/bin/bash
# Install wallpaper-selector-sync service

set -e

SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_NAME="wallpaper-selector-sync.service"

# Create directory if it doesn't exist
mkdir -p "$SERVICE_DIR"

# Copy service file
cp "$(dirname "$0")/$SERVICE_NAME" "$SERVICE_DIR/"

# Reload systemd
systemctl --user daemon-reload

# Enable service
echo "Enabling $SERVICE_NAME..."
systemctl --user enable "$SERVICE_NAME"

echo "Done! The wallpaper sync service will run on boot."
echo "You can test it now with: wallpaper-selector sync"
