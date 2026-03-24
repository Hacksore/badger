# Badge app repo — deploy + simulator helpers
#
# Defaults assume badgeware-simulator is cloned next to this repo:
#   code/
#     badger/              ← this repo
#     badgeware-simulator/ ← git clone, then: make -j  (first time)
#
# Override paths: `make deploy-sim BADGEWARE_SIM=~/src/badgeware-simulator`
# Or create `.env` from `.env.example`.

BADGER_MOUNT ?= /Volumes/BADGER
BADGEWARE_SIM ?= ../badgeware-simulator

export BADGER_MOUNT
export BADGEWARE_SIM

.PHONY: deploy deploy-badge deploy-sim sim help watch

help:
	@echo "Targets:"
	@echo "  deploy-badge  - rsync to \$BADGER_MOUNT (default $(BADGER_MOUNT))"
	@echo "  deploy-sim    - rsync into \$$BADGEWARE_SIM/root-badgeware"
	@echo "  deploy        - alias for deploy-badge"
	@echo "  sim           - deploy-sim then run ./go root in the simulator repo"
	@echo "  watch         - deploy-badge on each change (needs: brew install fswatch)"

deploy: deploy-badge

deploy-badge:
	@chmod +x scripts/deploy-badge.sh 2>/dev/null || true
	./scripts/deploy-badge.sh

deploy-sim:
	@chmod +x scripts/deploy-sim.sh 2>/dev/null || true
	./scripts/deploy-sim.sh

sim: deploy-sim
	@cd "$(BADGEWARE_SIM)" && ./go root

watch:
	@command -v fswatch >/dev/null || { echo "install fswatch: brew install fswatch"; exit 1; }
	fswatch -o . | while read -r _; do $(MAKE) deploy-badge; done
