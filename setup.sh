#!/usr/bin/bash

echo "-- Setting up CoordsTracker --"
# user="USER INPUT"
read -p "Your bot token: " TOKEN
echo "TOKEN=$TOKEN" >> .env
echo "PREFIX=!" >> .env

confirm=y
read -p "Continue installing virtual environment? (Y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

echo "Creating virtiual environment..."
python3 -m venv .venv

confirm=y
read -p "Continue installing pip packages? (Y/n): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
echo "Installing pip packages..."
.venv/bin/python3 -m pip install -r requirements.txt

echo ""
echo ""
echo "--- Bot is ready to run with .venv/bin/python3 CoordsTracker.py ---"


