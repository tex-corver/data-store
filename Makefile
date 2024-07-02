config_path = $(project_dir)/.configs
project_dir = $(shell pwd)

.PHONY: unit-test
unit-test:
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests/unit --junitxml=$(project_dir)/unit-test.xml

.PHONY: e2e-test
e2e-test:
	CONFIG_PATH=$(config_path) pytest $(project_dir)/tests/e2e --junitxml=$(project_dir)/e2e-test.xml

.PHONY: test
test: 
	CONFIG_PATH=$(config_path) pytest $(ops)