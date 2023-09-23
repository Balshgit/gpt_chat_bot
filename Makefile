# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

.DEFAULT_GOAL := help
.PHONY: help app format lint check-style check-import-sorting lint-typing lint-imports lint-complexity lint-deps

PY_TARGET_DIRS=bot_microservice settings
PORT=8000

## Запустить приложение
app:
	poetry run uvicorn --host 0.0.0.0 --factory bot_microservice.main:create_app --port $(PORT) --reload --reload-dir=bot_microservice --reload-dir=settings

## Отформатировать код
format:
	autoflake --recursive $(PY_TARGET_DIRS) --in-place --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports --remove-duplicate-keys --ignore-pass-statements
	pyup_dirs --py311-plus $(PY_TARGET_DIRS) | true
	isort --color --quiet $(PY_TARGET_DIRS)
	black $(PY_TARGET_DIRS)

## Проверить стилистику кода
check-style:
	black --check $(PY_TARGET_DIRS)

## Проверить сортировку импортов
check-import-sorting:
	isort --check-only $(PY_TARGET_DIRS)

## Проверить типизацию
lint-typing:
	mypy $(PY_TARGET_DIRS)

## Проверить код на сложность
lint-complexity:
	flake8 $(PY_TARGET_DIRS)

## Запустить все линтеры
lint: lint-typing lint-complexity check-import-sorting

## Проверить зависимостей
lint-deps:
	safety check --full-report && pip-audit

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = $$1; sub(/:$$/, "", helpCommand); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)25s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''
