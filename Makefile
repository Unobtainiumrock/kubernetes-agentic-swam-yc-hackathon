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

build:
	@${DOCKER_CMD} build --pull -t ${TAG_LATEST} -t ${TAG_GIT_SHA1} .

build-local:
	@${DOCKER_CMD} build --pull -t ${TAG_LATEST} .

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

# Streaming stack targets
stack-build:
	docker-compose build

stack-up:
	docker-compose up -d

stack-up-logs:
	docker-compose up

stack-down:
	docker-compose down

stack-logs:
	docker-compose logs -f

stack-restart:
	docker-compose restart

# Backend only
backend-build:
	docker-compose build backend

backend-up:
	docker-compose up -d backend

backend-logs:
	docker-compose logs -f backend

# Agent only
agent-build:
	docker-compose build autonomous-monitor

agent-up:
	docker-compose up -d autonomous-monitor

agent-logs:
	docker-compose logs -f autonomous-monitor

# Frontend only
frontend-build:
	docker-compose build frontend

frontend-up:
	docker-compose up -d frontend

frontend-logs:
	docker-compose logs -f frontend

# Full development stack
dev-up: stack-build
	@echo "🚀 Starting full development stack..."
	docker-compose up -d backend
	@echo "⏳ Waiting for backend to be healthy..."
	@until docker-compose exec backend curl -f http://localhost:8000/ > /dev/null 2>&1; do \
		echo "Waiting for backend..."; \
		sleep 2; \
	done
	@echo "✅ Backend is ready!"
	docker-compose up -d autonomous-monitor frontend
	@echo "🎉 Full stack is running!"
	@echo "📊 Frontend: http://localhost:3000"
	@echo "🔗 Backend: http://localhost:8000"
	@echo "📝 API Docs: http://localhost:8000/docs"

dev-logs:
	docker-compose logs -f

dev-down:
	docker-compose down

# Quick restart for development
dev-restart-agent:
	docker-compose restart autonomous-monitor

dev-restart-backend:
	docker-compose restart backend

# Clean up everything
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

push:
	${DOCKER_CMD} push ${TAG_LATEST}
	${DOCKER_CMD} push ${TAG_GIT_SHA1}
ifeq ($(GIT_BRANCH), $(CI_DEFAULT_BRANCH))
	${DOCKER_CMD} tag ${TAG_LATEST} ${DEFAULT_LATEST}
	${DOCKER_CMD} push ${DEFAULT_LATEST}
endif
