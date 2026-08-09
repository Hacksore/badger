SHELL := /bin/sh
.DEFAULT_GOAL := help

UV ?= uv
PYTHON = $(UV) run python
APP_NAME ?= badge
BADGER_MOUNT ?= $(firstword $(wildcard /Volumes/BADGER /Volumes/Badger2350 /Volumes/BADGER2350))
BOOT_MOUNT ?= $(firstword $(wildcard /Volumes/RP2350))
SIM_DIR ?= ../badgeware-simulator
BUILD_DIR ?= build
QR_URL ?= https://seanboult.dev
APP_FILES := __init__.py avatar.png social-qr.png
APP_DEST = $(BADGER_MOUNT)/apps/$(APP_NAME)
SIM_ROOT = $(abspath $(BUILD_DIR)/simulator-root)
RSYNC_FLAGS := -av --checksum

.PHONY: help setup qr check lint deploy sync-app deploy-dry-run watch backup \
	sim-setup sim-build sim-rebuild sim-deploy sim firmware firmware-full \
	flash-firmware flash-firmware-full clean

help: ## Show available commands (default)
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\n"} /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf '\nNormal workflow: double-tap RESET, then run `make deploy`.\n'

setup: ## Create/update the uv environment and install dev tools
	@command -v "$(UV)" >/dev/null 2>&1 || { echo "error: install uv from https://docs.astral.sh/uv/" >&2; exit 1; }
	$(UV) sync
	@$(MAKE) --no-print-directory qr

qr: ## Generate the social QR asset (override with QR_URL=https://...)
	$(PYTHON) tools/generate_qr.py "$(QR_URL)" social-qr.png

check: ## Validate Python syntax and required app files
	@$(PYTHON) tools/check_app.py $(APP_FILES)

lint: ## Run the uv-managed Ruff version
	$(UV) run ruff check .

deploy: sync-app ## Copy the app, safely eject it, and reboot the badge
	@if command -v diskutil >/dev/null 2>&1; then \
		diskutil eject "$(BADGER_MOUNT)"; \
	else \
		echo "Files synced. Safely eject $(BADGER_MOUNT) to reboot the badge."; \
	fi

sync-app: check ## Copy the app without ejecting (useful with watch)
	@$(MAKE) --no-print-directory _deploy RSYNC_EXTRA=

deploy-dry-run: check ## Preview exactly what deploy would copy
	@$(MAKE) --no-print-directory _deploy RSYNC_EXTRA=--dry-run

_deploy:
	@test -n "$(BADGER_MOUNT)" && test -d "$(BADGER_MOUNT)/apps" || { \
		echo "error: Badger disk mode drive not found." >&2; \
		echo "Double-tap RESET, or set BADGER_MOUNT=/path/to/drive." >&2; exit 1; \
	}
	@mkdir -p "$(APP_DEST)"
	rsync $(RSYNC_FLAGS) $(RSYNC_EXTRA) $(APP_FILES) "$(APP_DEST)/"
	@if test -z "$(RSYNC_EXTRA)"; then sync; echo "Deployed to $(APP_DEST)"; fi

watch: ## Deploy whenever an app file changes (requires fswatch)
	@command -v fswatch >/dev/null 2>&1 || { echo "error: install fswatch with: brew install fswatch" >&2; exit 1; }
	@fswatch -o $(APP_FILES) | while read event; do $(MAKE) --no-print-directory sync-app || true; done

backup: ## Back up the installed badge app into ./backups
	@test -n "$(BADGER_MOUNT)" && test -d "$(APP_DEST)" || { echo "error: badge app not found; enter disk mode first" >&2; exit 1; }
	@dest="backups/$(APP_NAME)-$$(date +%Y%m%d-%H%M%S)"; mkdir -p "$$dest"; rsync -av "$(APP_DEST)/" "$$dest/"; echo "Backed up to $$dest"

sim-setup: ## Clone and build Pimoroni's native Badgeware simulator
	@test ! -e "$(SIM_DIR)" || { echo "error: $(SIM_DIR) already exists" >&2; exit 1; }
	git clone --recurse-submodules https://github.com/pimoroni/badgeware-simulator.git "$(SIM_DIR)"
	$(MAKE) -C "$(SIM_DIR)" -j

sim-build: ## Build Pimoroni's native Badgeware simulator
	@test -d "$(SIM_DIR)" || { echo "error: simulator not found at $(SIM_DIR); run make sim-setup" >&2; exit 1; }
	@$(PYTHON) tools/patch_simulator.py "$(SIM_DIR)"
	@if test -x "$(SIM_DIR)/build/micropython" && test "$(SIM_DIR)/build/micropython" -nt "$(SIM_DIR)/micropython/main.c"; then \
		echo "Using existing simulator build at $(SIM_DIR)/build/micropython"; \
	else \
		$(MAKE) -C "$(SIM_DIR)" -j; \
	fi

sim-rebuild: ## Force a native simulator rebuild
	@test -d "$(SIM_DIR)" || { echo "error: simulator not found at $(SIM_DIR); run make sim-setup" >&2; exit 1; }
	@$(PYTHON) tools/patch_simulator.py "$(SIM_DIR)"
	$(MAKE) -C "$(SIM_DIR)" -j

sim-deploy: check ## Stage an isolated simulator filesystem with this app
	@test -d "$(SIM_DIR)/root-badgeware/system/apps" || { echo "error: simulator not found at $(SIM_DIR); run make sim-setup" >&2; exit 1; }
	@mkdir -p "$(SIM_ROOT)"
	rsync -a --delete "$(SIM_DIR)/root-badgeware/" "$(SIM_ROOT)/"
	@mkdir -p "$(SIM_ROOT)/system/apps/$(APP_NAME)"
	rsync $(RSYNC_FLAGS) $(APP_FILES) "$(SIM_ROOT)/system/apps/$(APP_NAME)/"
	rsync -a simulator/main.py "$(SIM_ROOT)/main.py"

sim: sim-build sim-deploy ## Build and run this app in Pimoroni's simulator
	@cd "$(SIM_DIR)" && ./build/micropython root="$(SIM_ROOT)" watch="$(SIM_ROOT)/system"

firmware: ## Download the latest non-erasing Badger firmware
	@$(PYTHON) tools/firmware.py download --output-dir "$(BUILD_DIR)"

firmware-full: ## Download the latest factory image (erases apps when flashed)
	@$(PYTHON) tools/firmware.py download --with-filesystem --output-dir "$(BUILD_DIR)"

flash-firmware: ## Flash latest firmware without replacing the filesystem
	@test -n "$(BOOT_MOUNT)" && test -d "$(BOOT_MOUNT)" || { \
		echo "error: RP2350 boot drive not found." >&2; \
		echo "Hold BOOT, tap RESET, release BOOT; or set BOOT_MOUNT=/path/to/RP2350." >&2; exit 1; \
	}
	@$(PYTHON) tools/firmware.py flash --mount "$(BOOT_MOUNT)" --output-dir "$(BUILD_DIR)"

flash-firmware-full: ## Factory reflash; requires ALLOW_ERASE=1 and wipes apps
	@test "$(ALLOW_ERASE)" = "1" || { echo "error: this wipes the badge; rerun with ALLOW_ERASE=1" >&2; exit 1; }
	@test -n "$(BOOT_MOUNT)" && test -d "$(BOOT_MOUNT)" || { echo "error: RP2350 boot drive not found" >&2; exit 1; }
	@$(PYTHON) tools/firmware.py flash --with-filesystem --mount "$(BOOT_MOUNT)" --output-dir "$(BUILD_DIR)"

clean: ## Remove downloaded firmware and Python caches
	rm -rf build __pycache__ tools/__pycache__
