.PHONY: dev build clean help

# Default target
help:
	@echo "Van LAN Router - Management Tasks"
	@echo ""
	@echo "Usage:"
	@echo "  make dev      Run the Flask app locally using 'uv'"
	@echo "  make build    Build the .deb package using Docker (MacOS/Linux)"
	@echo "  make clean    Remove build artifacts and virtual environment"

# Local development
dev:
	uv run app.py

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
