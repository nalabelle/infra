SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
print-%: ; @echo $*=$($*)

ANSIBLE_CACHE:=.ansible-cache
ANSIBLE_INVENTORY=ansible/inventory

.PHONY: help all clean deps clean-deps clean-cache
.DEFAULT_GOAL:=help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean-ansible
clean-ansible:
	rm -rf $(ANSIBLE_CACHE)
	rm inventory/group_vars/all/secrets.yaml

.PHONY: hetzner
hetzner:
	@ansible-playbook plays/infra/hetzner.yaml

.PHONY: server
server: inventory/group_vars/all/secrets.yaml
	@ansible-playbook plays/infra/server.yaml

.PHONY: inventory
inventory: $(ANSIBLE_CACHE)/hosts

$(ANSIBLE_CACHE)/hosts:
	@mkdir -p $(ANSIBLE_CACHE)
	@ansible-inventory --list | jq 'with_entries(select(.key != "_meta"))' > $(ANSIBLE_CACHE)/hosts


clean: clean-deps clean-ansible ## Reset all generated files
	@rm .env.secrets
	@rm -r .bin

# Secret
.PHONY: secrets clean-secrets
secrets: .env.secrets inventory/group_vars/all/secrets.yaml
	@true
clean-secrets:
	@rm -f .env.secrets
	@rm -f inventory/group_vars/all/secrets.yaml
inventory/group_vars/all/secrets.yaml: inventory/group_vars/all/secrets.yaml.tpl
	@op inject -f -i $< -o $@
.env.secrets: .env.secrets.tpl
	@op inject -f -i $< -o $@

# Vendor
.PHONY: clean-vendor
vendor:
	@vendir sync
clean-vendor:
	rm -rf vendor
