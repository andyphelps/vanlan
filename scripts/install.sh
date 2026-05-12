#!/bin/bash
set -e

# VanLAN Router Repository Setup Script
# This script adds the VanLAN Apt repository to your system.

REPO_URL="https://andyphelps.github.io/vanlan"
KEY_PATH="/etc/apt/trusted.gpg.d/vanlan.gpg"
LIST_PATH="/etc/apt/sources.list.d/vanlan.list"

echo "--- VanLAN Router: Repository Setup ---"

# 1. Check for root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# 2. Install dependencies
echo "Checking dependencies..."
apt-get update -qq
apt-get install -y -qq curl gpg > /dev/null

# 3. Download and install GPG key
echo "Downloading repository key..."
curl -fsSL "${REPO_URL}/public.key" | gpg --dearmor | tee "$KEY_PATH" > /dev/null

# 4. Add repository to sources list
echo "Adding repository to sources list..."
echo "deb ${REPO_URL}/ trixie main" | tee "$LIST_PATH" > /dev/null

# 5. Update apt
echo "Updating package lists..."
apt-get update -qq

echo "---------------------------------------"
echo "Setup complete! You can now install VanLAN Router with:"
echo "  sudo apt install vanlan-router"
echo "---------------------------------------"
