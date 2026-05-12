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

# 2. Clean up old/broken setup if it exists
if [ -f "$LIST_PATH" ]; then
    echo "Removing previous repository configuration..."
    rm -f "$LIST_PATH"
fi

# 3. Install dependencies
echo "Checking dependencies..."
# Use -o to ignore the broken repo we just removed if apt still has it in cache
apt-get update -o Dir::Etc::sourcelist="$LIST_PATH" -o Dir::Etc::sourceparts="-" -qq || true
apt-get install -y -qq curl gpg > /dev/null

# 4. Download and install GPG key
echo "Downloading repository key..."
# Try to fetch the key, handle 404 if GitHub Pages isn't ready yet
if ! curl -fsSL "${REPO_URL}/public.key" | gpg --dearmor | tee "$KEY_PATH" > /dev/null; then
    echo "Error: Could not download the repository key."
    echo "GitHub Pages might still be deploying. Please wait a minute and try again."
    exit 1
fi

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
