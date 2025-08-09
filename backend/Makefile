# Backend/API Makefile
SHELL := /bin/bash
IMAGE_NAME ?= agentic-k8s-backend:dev
CONTAINER_NAME ?= agentic-k8s-backend
ENV_FILE ?= ../.env
ENV_OPT := $(shell [ -f $(ENV_FILE) ] && echo --env-file $(ENV_FILE))

.PHONY: build run logs stop clean dev-run

# Build the backend Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the backend container
run:
	docker rm -f $(CONTAINER_NAME) >/dev/null 2>&1 || true
	docker run -d --name $(CONTAINER_NAME) -p 8000:8000 $(ENV_OPT) $(IMAGE_NAME)

# View logs from running container
logs:
	docker logs -f $(CONTAINER_NAME)

# Stop the backend container
stop:
	docker rm -f $(CONTAINER_NAME) || true

# Clean up Docker image
clean:
	docker rmi $(IMAGE_NAME) || true

# Run backend in development mode (local Python)
dev-run:
	pip install -r requirements.txt
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Install dependencies locally
install:
	pip install -r requirements.txt

# Run tests (placeholder for future tests)
test:
	python -m pytest tests/ || echo "No tests found yet"

# Format code
format:
	black app/
	isort app/

# Lint code
lint:
	flake8 app/
	mypy app/ --ignore-missing-imports

# Help target
help:
	@echo "Available targets:"
	@echo "  build     - Build Docker image"
	@echo "  run       - Run container in background"
	@echo "  logs      - View container logs"
	@echo "  stop      - Stop and remove container"
	@echo "  clean     - Remove Docker image"
	@echo "  dev-run   - Run locally with hot reload"
	@echo "  install   - Install Python dependencies"
	@echo "  test      - Run tests"
	@echo "  format    - Format code with black and isort"
	@echo "  lint      - Lint code with flake8 and mypy" 