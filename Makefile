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
	docker run --rm -v "$$(pwd)/..:/build-output" vanlan-builder sh -c "cp ../vanlan-router_*.deb /build-output/ 2>/dev/null || true"
	@echo "Build complete. Check the parent directory for the .deb file."

# Clean up
clean:
	rm -rf .venv
	rm -f build_on_mac.sh
	@echo "Cleaned up."
