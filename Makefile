.PHONY: install clean lint format lock-dependencies install-dev build test-run run venv

## Install for production
install:
	@echo ">> Installing dependencies"
	python -m pip install --upgrade pip
	python -m pip install -e .

## Install for development
install-dev: install
	python -m pip install -e ".[dev]"

## Delete all temporary files
clean:
	rm -rf .ipynb_checkpoints
	rm -rf **/.ipynb_checkpoints
	rm -rf .pytest_cache
	rm -rf **/.pytest_cache
	rm -rf __pycache__
	rm -rf **/__pycache__
	rm -rf build
	rm -rf dist

## Get project version
# grep the version from pyproject.toml, squeeze multiple spaces, delete double
#   and single quotes, get 3rd val. This command tolerates
#   multiple whitespace sequences around the version number
VERSION := $(shell grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)

## Lint using ruff
ruff:
	ruff .

## Format files using black
format:
	black .
	ruff format .

## Run tests
test:
	pytest --cov=courtbooker --cov-report xml --log-level=WARNING --disable-pytest-warnings

## Run checks (ruff + test)
check:
	ruff check .
	black --check .

## Update dependencies
lock-dependencies:
	pip-compile --generate-hashes --output-file=requirements.txt pyproject.toml
	pip-compile --generate-hashes --extra=dev --output-file=requirements-dev.txt pyproject.toml

sync-dependencies: lock-dependencies install-dev

## Build docker image
build:
	docker build -t courtbooker:$(VERSION) .
	docker tag courtbooker:$(VERSION) courtbooker:latest

## Test run
test-run:
	docker-compose start postgres
	docker build -t courtbooker:test .
	docker run --entrypoint python --env-file .env.test courtbooker:test main.py

## Run api
run:
	docker run --entrypoint python --env-file .env courtbooker:latest main.py

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available commands:$$(tput sgr0)"
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
