IMAGE_NAME ?= dfkozlov/adk-agent-api:dev
ENV_FILE ?= /Users/chalmers/code/kubernetes-agentic-swam-yc-hackathon/google-adk/.env
ENV_OPT := $(shell [ -f $(ENV_FILE) ] && echo --env-file $(ENV_FILE))

.PHONY: api-build api-run api-logs api-stop api-clean

api-build:
	cd .. && docker build -f api/Dockerfile -t $(IMAGE_NAME) .

api-run:
	docker rm -f adk-api >/dev/null 2>&1 || true
	docker run -d --name adk-api -p 8080:8000 $(ENV_OPT) $(IMAGE_NAME)

api-logs:
	docker logs -f adk-api

api-stop:
	docker rm -f adk-api || true

api-clean:
	docker rmi $(IMAGE_NAME) || true

api-push:
	docker push $(IMAGE_NAME) || true
