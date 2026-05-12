.PHONY: build clean help

# VanLAN Router Makefile
# This file is used for CI builds and local cleanup.

# Default target
help:
	@echo "Van LAN Router - Management Tasks"
	@echo ""
	@echo "Usage:"
	@echo "  make clean    Remove build artifacts and virtual environment"

# Build the Debian package using Docker
build:
	docker build -t vanlan-builder -f Dockerfile.build .
	docker run --rm -v "$$(pwd):/output" vanlan-builder
	@echo "Build complete. Check the current directory for the .deb file."

# Clean up
clean:
	rm -rf .venv
	rm -f vanlan-router_*.deb
	rm -f vanlan-router_*.changes
	rm -f vanlan-router_*.buildinfo
	@echo "Cleaned up."
