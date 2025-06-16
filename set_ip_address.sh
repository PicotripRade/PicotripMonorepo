#!/bin/bash

# Get the first IP address listed by `hostname -I`
IP=$(hostname -I | awk '{print $1}')

# Update backend/settings.py
sed -i "s/^VITE_URL=.*$/VITE_URL=${IP}/" .env

echo "Updated IP address to ${IP}"