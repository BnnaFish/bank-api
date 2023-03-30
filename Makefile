# commands
lint: mypy flake8

mypy:
	@mypy app

flake8:
	@flake8 app

test:
	@pytest ./tests/unit

test_integration:
	@pytest ./tests/integration

isort:
	isort --atomic .

# docker: control services
stop:
	@docker compose stop

down:
	@docker compose down -v --remove-orphans

# docker: built containers
build.dev:
	@docker compose build dev

build.test:
	@docker compose build test

build.test_integration:
	@docker compose build test_integration

build.bash:
	@docker compose build bash

# docker: exec
bash:
	@docker compose run bash sh

# docker: commands
dc.isort: build.bash
	@docker compose run bash make isort;

dc.flake8: stop build.test
	@docker compose run test make flake8;

dc.lint: stop build.test
	@docker compose run test make lint;

dc.test: stop build.test
	@docker compose run test make test;
	@docker compose run test make lint;
	@docker compose stop;

dc.test_integration: stop build.test_integration
	@docker compose run test_integration make test_integration;
	@docker compose stop;

dc.run: stop build.dev
	@docker compose up dev
