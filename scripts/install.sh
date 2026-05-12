#!/bin/bash
set -eo pipefail

# VanLAN Router Repository Setup Script
# This script adds the VanLAN Apt repository to your system.

REPO_URL="https://andyphelps.github.io/vanlan"
KEYRING_PATH="/usr/share/keyrings/vanlan-archive-keyring.gpg"
LIST_PATH="/etc/apt/sources.list.d/vanlan.list"
OLD_KEY_PATH="/etc/apt/trusted.gpg.d/vanlan.gpg"

echo "--- VanLAN Router: Repository Setup ---"

# 1. Check for root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# 2. Clean up old/broken setup if it exists
echo "Cleaning up old configurations..."
rm -f "$LIST_PATH"
rm -f "$OLD_KEY_PATH"

# 3. Install dependencies
echo "Checking dependencies (curl, gpg)..."
apt-get update -qq || true
apt-get install -y -qq curl gpg > /dev/null

# 4. Download and install GPG key using modern signed-by approach
echo "Downloading and installing repository key..."
if ! curl -fsSL "${REPO_URL}/public.key" | gpg --dearmor | tee "$KEYRING_PATH" > /dev/null; then
    echo "Error: Could not download the repository key."
    echo "GitHub Pages might still be deploying or there is a network issue."
    exit 1
fi

# 5. Add repository to sources list with signed-by
echo "Adding repository to sources list..."
echo "deb [signed-by=$KEYRING_PATH] ${REPO_URL}/ trixie main" | tee "$LIST_PATH" > /dev/null

# 6. Update apt
echo "Updating package lists..."
apt-get update -o Dir::Etc::sourcelist="$LIST_PATH" -o Dir::Etc::sourceparts="-" -qq

echo "---------------------------------------"
echo "Setup complete! You can now install VanLAN Router with:"
echo "  sudo apt install vanlan-router"
echo "---------------------------------------"
