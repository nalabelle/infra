SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
print-%: ; @echo $*=$($*)

ANSIBLE_CACHE:=.ansible-cache
.DEFAULT_GOAL:=help

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean
clean: clean-deps clean-ansible-cache clean-secrets ## Reset all generated files
	@true

.PHONY: playbook
playbook: plays/*.yaml vendor secrets
	@ansible-playbook \
		plays/hetzner.yaml \
		plays/hetzner_server.yaml \
		plays/compose_hosts.yaml

.PHONY: clean-ansible-cache
clean-ansible-cache:
	@rm -rf $(ANSIBLE_CACHE)

.PHONY: inventory
inventory: $(ANSIBLE_CACHE)/hosts vendor .env.secrets
$(ANSIBLE_CACHE)/hosts:
	@mkdir -p $(ANSIBLE_CACHE)
	@ansible-inventory --list | jq 'with_entries(select(.key != "_meta"))' > $(ANSIBLE_CACHE)/hosts

# Secret
.PHONY: secrets clean-secrets
secrets: .env.secrets inventory/group_vars/all/secrets.yaml .secrets/hosts
	@true
clean-secrets:
# Clean this up manually
# @rm -f .env.secrets
	@rm -f inventory/group_vars/all/secrets.yaml
inventory/host_vars/%.yaml: inventory/host_vars/_host.yaml.tpl
	@HOSTNAME=$(basename $(notdir $@)) op inject -f -i $< -o $@

inventory/group_vars/all/secrets.yaml: inventory/group_vars/all/secrets.yaml.tpl
	@op inject -f -i $< -o $@
.env.secrets: .env.secrets.tpl
	@op inject -f -i $< -o $@
.secrets/hosts: .secrets
	op read -o .secrets/hosts op://Applications/HOSTS/file
.secrets:
	mkdir -p .secrets

# Vendor
.PHONY: clean-vendor
vendor:
	@vendir sync
clean-vendor:
	rm -rf vendor
