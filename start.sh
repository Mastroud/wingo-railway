#!/bin/bash

# Install Chrome inside Railway container
apt-get update && apt-get install -y wget unzip curl
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Run scraper
while true; do
  python3 cloud_scraper.py
  sleep 1
done

