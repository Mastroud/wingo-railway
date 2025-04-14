#!/bin/bash
playwright install chromium
while true; do
  python3 cloud_scraper.py
  sleep 1
done

