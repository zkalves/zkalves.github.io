.DEFAULT_GOAL := help
.PHONY: help preview dev serve jekyll-install jekyll-serve docker-serve check clean distclean

PORT ?= 4000
PYTHON ?= python3
BUNDLE ?= $(shell which bundle3.3 2>/dev/null || which bundle 2>/dev/null || echo bundle)

help: ## Show this help menu
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

preview: ## Start zero-dependency local preview server (http://localhost:4000)
	$(PYTHON) preview.py

dev: preview ## Alias for 'preview'

serve: preview ## Alias for 'preview'

jekyll-install: ## Install Ruby dependencies locally into vendor/bundle
	$(BUNDLE) config set --local path 'vendor/bundle'
	$(BUNDLE) install

jekyll-serve: ## Start native Jekyll server with live reload via Bundler
	$(BUNDLE) exec jekyll serve --livereload --port $(PORT)

docker-serve: ## Start preview using official Jekyll Docker image
	docker run --rm -v "$$PWD:/srv/jekyll" -p $(PORT):4000 -it jekyll/jekyll:pages jekyll serve

check: ## Validate YAML configuration and template integrity
	@$(PYTHON) -c "import yaml; yaml.safe_load(open('_config.yml')); print('YAML syntax: OK')"
	@$(PYTHON) -c "import preview; preview.build_html(); print('Template rendering: OK')"

clean: ## Remove Jekyll build artifacts and temporary cache directories
	rm -rf _site .jekyll-cache .jekyll-metadata .sass-cache
	@echo "Cleaned build artifacts."

distclean: clean ## Remove all build artifacts, vendor gems, and bundler config
	rm -rf vendor/ .bundle/
	@echo "Cleaned all vendor dependencies."
