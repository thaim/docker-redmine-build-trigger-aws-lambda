PACKAGE_NAME = docker-redmine-build-trigger

include .env

.PHONY: help package deploy

help: ## show this help.
	@echo "Please use \`make <target>' where <target> is one of\n"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

package: ## create zip archive to deploy
	pip install -r requirements.txt -t .
	zip -r $(PACKAGE_NAME).zip *

deploy: ## deploy function to aws lambda
	if 	aws lambda list-functions | jq .Functions[].FunctionName | grep -c ^\"$(PACKAGE_NAME)\"$$ > 0; then \
		aws lambda update-function-code \
			--function-name $(PACKAGE_NAME) \
			--zip-file fileb://$(PACKAGE_NAME).zip; \
	else \
		aws lambda create-function \
			--function-name $(PACKAGE_NAME) \
			--runtime python3.6 \
			--role $(AWS_ROLE) \
			--handler trigger.lambda_handler \
			--zip-file fileb://$(PACKAGE_NAME).zip \
			--region ap-northeast-1; \
	fi



clean: ## remove archive files and package files
	rm -f *.whl *.tar.gz *.zip *~
	find . -maxdepth 1 -type d | grep -v -e '\.git$$' -e '\.$$' | xargs rm -r
