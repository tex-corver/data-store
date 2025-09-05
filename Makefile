project_dir = $(shell pwd)
config_path = $(project_dir)/.configs
docs_dir = $(project_dir)/docs
build_dir = $(project_dir)/_build

.PHONY: unit-test
unit-test:
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests/unit --junitxml=$(project_dir)/unit-test.xml

.PHONY: e2e-test
e2e-test:
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests/e2e --junitxml=$(project_dir)/e2e-test.xml

.PHONY: test
test:
	CONFIG_PATH=$(config_path) pytest $(o)

# Documentation targets
.PHONY: docs-build
docs-build:
	@echo "Building Sphinx documentation..."
	@cd $(docs_dir) && poetry run sphinx-build -b html . $(build_dir)
	@echo "Documentation built successfully in $(build_dir)/index.html"

.PHONY: docs-serve
docs-serve: docs-build
	@echo "Starting documentation server..."
	@cd $(build_dir) && python3 -m http.server 8000
	@echo "Documentation server running at http://localhost:8000"

.PHONY: docs-clean
docs-clean:
	@echo "Cleaning documentation build artifacts..."
	@rm -rf $(build_dir)
	@echo "Documentation build artifacts cleaned"

.PHONY: docs
docs: docs-serve

.PHONY: docs-live
docs-live:
	@echo "Starting live documentation server with auto-reload..."
	@cd $(docs_dir) && poetry run sphinx-autobuild -b html . $(build_dir)