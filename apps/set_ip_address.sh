#!/bin/bash

# Get the first IP address listed by `hostname -I`
IP=$(hostname -I | awk '{print $1}')

# Update react-frontend/.env
# Assuming the .env file path is relative to the script location, adjust if necessary
sed -i "s/^REACT_APP_URL=.*$/REACT_APP_URL=${IP}/" web/.env

# Update backend/settings.py
sed -i "s/^URL=.*$/URL=${IP}/" .env

echo "Updated IP address to ${IP}"