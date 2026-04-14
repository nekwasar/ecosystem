.PHONY: help up down restart logs ps test-db clean networks

help:
	@echo "Ecosystem Docker Commands"
	@echo "========================"
	@echo "make up         - Start all infrastructure services"
	@echo "make down       - Stop all services"
	@echo "make restart    - Restart all services"
	@echo "make logs       - View logs"
	@echo "make ps         - Show running containers"
	@echo "make test-db    - Test PostgreSQL connection"
	@echo "make clean     - Remove all containers and volumes"
	@echo "make networks   - Show Docker networks"

up:
	@echo "Starting infrastructure services..."
	cd $(dir $(abspath $(lastword $(MAKEFILE_LIST)))) && docker compose up -d

down:
	@echo "Stopping services..."
	cd $(dir $(abspath $(lastword $(MAKEFILE_LIST)))) && docker compose down

restart: down up

logs:
	cd $(dir $(abspath $(lastword $(MAKEFILE_LIST)))) && docker compose logs -f

ps:
	docker compose -f $(abspath $(lastword $(MAKEFILE_LIST)))/docker-compose.yml ps

test-db:
	@echo "Testing PostgreSQL connection..."
	@docker exec -it ecosystem_postgres pg_isready -U ecosystem || echo "PostgreSQL not ready"
	@echo "Listing databases..."
	@docker exec -it ecosystem_postgres psql -U ecosystem -l

clean:
	@echo "Removing all containers and volumes..."
	docker compose -f $(abspath $(lastword $(MAKEFILE_LIST)))/docker-compose.yml down -v
	@echo "Clean complete"

networks:
	@echo "Docker networks:"
	@docker network ls | grep ecosystem
