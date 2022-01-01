.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: up
up: ## Up application
	docker-compose up --build --remove-orphans --abort-on-container-exit -t 0 ld_redis db local_delivery_bot


.PHONY: down
down: ## Stop development environment
	docker-compose down --remove-orphans -t 0

