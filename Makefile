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


push:
	${DOCKER_CMD} push ${TAG_LATEST}
	${DOCKER_CMD} push ${TAG_GIT_SHA1}
ifeq ($(GIT_BRANCH), $(CI_DEFAULT_BRANCH))
	${DOCKER_CMD} tag ${TAG_LATEST} ${DEFAULT_LATEST}
	${DOCKER_CMD} push ${DEFAULT_LATEST}
endif
