TOKEN ?= JIRA_TOKEN

.DEFAULT_GOAL := explain
explain:
	### Welcome
    # Makefile for the JIRA Project Burndown to Slack application
	#
	#  _                          _
	# | |__  _   _ _ __ _ __   __| | _____      ___ __
	# | '_ \| | | | '__| '_ \ / _` |/ _ \ \ /\ / / '_ \
# | |_) | |_| | |  | | | | (_| | (_) \ V  V /| | | |
	# |_.__/ \__,_|_|  |_| |_|\__,_|\___/ \_/\_/ |_| |_|
	#
	#
	### Installation
	#
	# Install Python Dependencies for the Project
	#  -> $$ make install-python-deps
	#
	#
	### Daily Burn Down
	#
	# To Get Daily BurnDown
	#  -> $$ make daily-burn-down
	#
	#  Note: Make sure you have provided the necessary parameters in MAKEFILE
	#
	### To know Required Parameters
	#
	# Run the following
	#  -> $$ make required-params
	#  Note: Make sure you have provided the necessary parameters in MAKEFILE
	#
	### Targets
	#
	@cat Makefile* | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install-python-deps
install-python-deps: ## Install Python Dependencies
	pip install -r requirements.txt

.PHONY: daily-burn-down
daily-burn-down: ## Get the Burndown
	python daily-burn-down.py -a $(TOKEN)

.PHONY: required-params
required-params: ## Know the Required Parameters
	python daily-burn-down.py
