BADGER_MOUNT ?= /Volumes/BADGER

# Set SYNC_DELETE=1 to remove files on the badge that are not in this folder (use carefully).
RSYNC_DELETE := $(if $(filter 1,$(SYNC_DELETE)),--delete,)

.PHONY: deploy

deploy:
	@test -d "$(BADGER_MOUNT)" || { echo "error: not mounted: $(BADGER_MOUNT)"; exit 1; }
	mkdir -p "$(BADGER_MOUNT)/apps/badge"
	rsync -a $(RSYNC_DELETE) \
		--exclude '.git' \
		--exclude '.DS_Store' \
		--exclude 'Makefile' \
		--exclude '.gitignore' \
		--exclude '.env' \
		"$(CURDIR)/" "$(BADGER_MOUNT)/apps/badge/"
	sync
	@echo "-> $(BADGER_MOUNT)/apps/badge/"
