SHELL          := /bin/bash
REGISTRY       := dfkozlov
NAME           := k8s-agentic-swarm-command-center
GIT_BRANCH     := $(shell if [ -n "$$CI_COMMIT_REF_NAME" ]; then echo "$$CI_COMMIT_REF_NAME"; else git rev-parse --abbrev-ref HEAD; fi)
GIT_BRANCH     := $(shell echo "${GIT_BRANCH}" | tr '[:upper:]' '[:lower:]')
GIT_SHA1       := $(shell git rev-parse HEAD)
CONTAINER_NAME := ${NAME}-${GIT_BRANCH}
IMAGE_NAME     := ${REGISTRY}/${NAME}
TAG_GIT_SHA1   := ${IMAGE_NAME}:${GIT_BRANCH}-${GIT_SHA1}
TAG_LATEST     := ${IMAGE_NAME}:${GIT_BRANCH}-latest
DEFAULT_LATEST := ${IMAGE_NAME}:latest
DOCKER_CMD     := docker

# Container build targets
build:
	@${DOCKER_CMD} build --pull -t ${TAG_LATEST} -t ${TAG_GIT_SHA1} .

build-local:
	@${DOCKER_CMD} build --pull -t ${TAG_LATEST} .

# Development container targets
run:
	git submodule update --init --recursive
	rm -rf $$(pwd)/.ansible
	${DOCKER_CMD} rm -f ${CONTAINER_NAME} || true
	${DOCKER_CMD} run -it --privileged --rm -v /var/run/docker.sock:/var/run/docker.sock --network=host --pull always --name ${CONTAINER_NAME} -e DOCKER_UID=$$(id -u) -e DOCKER_GID=$$(id -g) -v $$(pwd):/root ${TAG_LATEST} bash

run-local:
	rm -rf $$(pwd)/.ansible
	${DOCKER_CMD} rm -f ${CONTAINER_NAME} || true
	${DOCKER_CMD} run -it --privileged --rm -v /var/run/docker.sock:/var/run/docker.sock --network=host --pull never --name ${CONTAINER_NAME} -e DOCKER_UID=$$(id -u) -e DOCKER_GID=$$(id -g) -v $$(pwd):/root ${TAG_LATEST} bash

exec:
	${DOCKER_CMD} exec -it ${CONTAINER_NAME} bash

exec-user:
	${DOCKER_CMD} exec -it -u $$(id -u):$$(id -g) ${CONTAINER_NAME} bash

# Run container and automatically start streaming stack
run-local-with-stack:
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME} \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-p 8000:8000 \
		--network host \
		${IMAGE_NAME} bash -c "cd /root && ./scripts/run-streaming-stack.sh"

# Cluster management targets (container-first)
setup-cluster: build-local
	@echo "🏗️  Setting up Kubernetes cluster (container-first)..."
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME}-setup \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./scripts/setup-cluster.sh"

deploy-demo-apps: 
	@echo "🚀 Deploying demo applications..."
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME}-deploy \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./scripts/deploy-demo-apps.sh"

cleanup-cluster:
	@echo "🧹 Cleaning up Kubernetes cluster..."
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME}-cleanup \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./scripts/cleanup.sh"

# Full development stack - Pure container-first approach
start-fullstack: build-local
	@echo "🚀 Starting Full Stack Application (Pure Container-First)"
	@echo "=========================================================="
	@echo "🐳 Backend: Running in container with AI agents"
	@echo "⚛️  Frontend: Running in container with hot reload"
	@echo "☸️  Cluster: Managed via containers"
	@echo ""
	${DOCKER_CMD} run -it --rm --name k8s-fullstack-container \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-p 3000:3000 -p 8000:8000 \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./scripts/start-fullstack-container.sh"

# Legacy approach for comparison
dev-up: build-local
	@echo "🚀 Starting development stack (hybrid approach)..."
	@echo "📋 This will start using host + container hybrid"
	@echo "   Run: ./start-fullstack.sh"

# Clean up everything - Full stack shutdown
clean:
	@echo "🧹 Complete Full Stack Cleanup"
	@echo "================================"
	@echo "🛑 Stopping full stack application..."
	
	# Stop frontend processes
	@pkill -f "vite.*3000" 2>/dev/null || echo "   Frontend already stopped"
	@pkill -f "npm.*dev" 2>/dev/null || echo "   NPM dev server already stopped"
	
	# Stop backend containers
	@echo "🐳 Stopping backend containers..."
	${DOCKER_CMD} stop k8s-dev-container 2>/dev/null || echo "   Backend container already stopped"
	${DOCKER_CMD} rm k8s-dev-container 2>/dev/null || echo "   Backend container already removed"
	${DOCKER_CMD} stop k8s-fullstack-container 2>/dev/null || echo "   Fullstack container already stopped"
	${DOCKER_CMD} rm k8s-fullstack-container 2>/dev/null || echo "   Fullstack container already removed"
	${DOCKER_CMD} stop ${CONTAINER_NAME} 2>/dev/null || echo "   Dev container already stopped"
	${DOCKER_CMD} rm ${CONTAINER_NAME} 2>/dev/null || echo "   Dev container already removed"
	
	# Clean up Kubernetes cluster
	@echo "☸️  Removing Kubernetes cluster..."
	@kind delete cluster --name demo-cluster 2>/dev/null || echo "   Cluster already removed"
	
	# Clean up Docker resources
	@echo "🐳 Cleaning up Docker resources..."
	${DOCKER_CMD} system prune -f
	
	@echo "✅ Complete cleanup finished!"

# Light cleanup - Containers only (no cluster)
clean-containers:
	@echo "🧹 Cleaning up containers only..."
	${DOCKER_CMD} stop ${CONTAINER_NAME} k8s-dev-container 2>/dev/null || true
	${DOCKER_CMD} rm ${CONTAINER_NAME} k8s-dev-container 2>/dev/null || true
	${DOCKER_CMD} system prune -f

# Push targets
push:
	${DOCKER_CMD} push ${TAG_LATEST}
	${DOCKER_CMD} push ${TAG_GIT_SHA1}
ifeq ($(GIT_BRANCH), $(CI_DEFAULT_BRANCH))
	${DOCKER_CMD} tag ${TAG_LATEST} ${DEFAULT_LATEST}
	${DOCKER_CMD} push ${DEFAULT_LATEST}
endif

# Help target
help:
	@echo "🚀 Container-First Development Commands:"
	@echo "  make build-local     - Build development container"
	@echo "  make run-local       - Run interactive container"
	@echo ""
	@echo "🏗️  Cluster Management (Container-First):"
	@echo "  make setup-cluster   - Create Kubernetes cluster (in container)"
	@echo "  make deploy-demo-apps - Deploy demo applications (in container)"
	@echo "  make cleanup-cluster - Remove Kubernetes cluster (in container)"
	@echo ""
	@echo "🧹 Cleanup Options:"
	@echo "  make clean           - 🚨 COMPLETE cleanup (apps + cluster + containers)"
	@echo "  make clean-containers - Light cleanup (containers only, keeps cluster)"
	@echo "  ./cleanup-fullstack.sh - Script-based complete cleanup"
	@echo ""
	@echo "🎯 Pure Container-First Workflow (Recommended):"
	@echo "  make setup-cluster      - Set up K8s cluster"
	@echo "  make deploy-demo-apps   - Deploy demo applications"
	@echo "  make start-fullstack    - 🚀 Start full stack (pure container)"
	@echo "  make clean              - Complete cleanup when done"
	@echo ""
	@echo "🔧 Alternative Commands:"
	@echo "  ./start-fullstack.sh         - Hybrid approach (host + container)"
	@echo "  ./chaos-scenarios.sh         - Manual chaos engineering"
	@echo "  ./scripts/setup-cluster.sh   - Direct script (requires host tools)"

.PHONY: build build-local run run-local exec exec-user run-local-with-stack start-fullstack dev-up clean clean-containers push help
