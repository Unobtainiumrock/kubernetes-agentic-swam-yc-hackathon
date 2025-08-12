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
		${IMAGE_NAME} bash -c "cd /root && ./run-streaming-stack.sh"

# Cluster management targets (container-first)
setup-cluster: build-local
	@echo "🏗️  Setting up Kubernetes cluster (container-first)..."
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME}-setup \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./setup-cluster.sh"

deploy-demo-apps: 
	@echo "🚀 Deploying demo applications..."
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME}-deploy \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./deploy-demo-apps.sh"

cleanup-cluster:
	@echo "🧹 Cleaning up Kubernetes cluster..."
	${DOCKER_CMD} run -it --rm --name ${CONTAINER_NAME}-cleanup \
		-v ${PWD}:/root \
		-v ${HOME}/.kube:/root/.kube \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--network host \
		${TAG_LATEST} bash -c "cd /root && ./cleanup.sh"

# Full development stack - Container first approach
dev-up: build-local
	@echo "🚀 Starting full development stack (container-first)..."
	@echo "📋 This will start the full stack using containers"
	@echo "   Run: ./start-fullstack.sh"

# Clean up everything
clean:
	@echo "🧹 Cleaning up containers and images..."
	${DOCKER_CMD} stop ${CONTAINER_NAME} 2>/dev/null || true
	${DOCKER_CMD} rm ${CONTAINER_NAME} 2>/dev/null || true
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
	@echo "  make clean          - Clean up containers"
	@echo ""
	@echo "🏗️  Cluster Management (Container-First):"
	@echo "  make setup-cluster   - Create Kubernetes cluster (in container)"
	@echo "  make deploy-demo-apps - Deploy demo applications (in container)"
	@echo "  make cleanup-cluster - Remove Kubernetes cluster (in container)"
	@echo ""
	@echo "🎯 Recommended Full Workflow:"
	@echo "  make setup-cluster      - Set up K8s cluster"
	@echo "  ./start-fullstack.sh    - Start application"
	@echo "  ./cleanup-fullstack.sh  - Complete cleanup"
	@echo ""
	@echo "🔧 Alternative Commands:"
	@echo "  ./setup-cluster.sh      - Direct script (requires host tools)"
	@echo "  ./start-fullstack.sh    - Start application"

.PHONY: build build-local run run-local exec exec-user run-local-with-stack dev-up clean push help
