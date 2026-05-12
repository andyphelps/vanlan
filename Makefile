.PHONY: build deploy clean help

# Default target
help:
	@echo "Van LAN Router - Management Tasks"
	@echo ""
	@echo "Usage:"
	@echo "  make deploy   Build and SCP the package to 'vanlan'"
	@echo "  make clean    Remove build artifacts and virtual environment"

# Build the Debian package using Docker
build:
	docker build -t vanlan-builder -f Dockerfile.build .
	docker run --rm -v "$$(pwd):/output" vanlan-builder
	@echo "Build complete. Check the current directory for the .deb file."

# Deploy to vanlan
deploy: build
	scp vanlan-router_*.deb 10.42.0.1:~/
	@echo "Package deployed to vanlan. Install it with: sudo dpkg -i ~/vanlan-router_*.deb"

# Clean up
clean:
	rm -rf .venv
	rm -f vanlan-router_*.deb
	rm -f vanlan-router_*.changes
	rm -f vanlan-router_*.buildinfo
	@echo "Cleaned up."
