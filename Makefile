BADGER_MOUNT ?= /Volumes/BADGER

.PHONY: deploy

deploy:
	@test -d "$(BADGER_MOUNT)" || { echo "error: not mounted: $(BADGER_MOUNT)"; exit 1; }
	mkdir -p "$(BADGER_MOUNT)/apps/badge"
	cp __init__.py "$(BADGER_MOUNT)/apps/badge/__init__.py"
	sync
	@echo "-> $(BADGER_MOUNT)/apps/badge/__init__.py"
