#!/bin/bash
sudo apt update
sudo apt install -y chromium-browser chromium-chromedriver
pip install -r requirements.txt
python3 cloud_scraper.py
