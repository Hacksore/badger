SHELL := /bin/sh
.DEFAULT_GOAL := help

UV ?= uv
PYTHON = $(UV) run python
BADGER_MOUNT ?= $(firstword $(wildcard /Volumes/BADGER /Volumes/Badger2350 /Volumes/BADGER2350))
BOOT_MOUNT ?= $(firstword $(wildcard /Volumes/RP2350))
SIM_DIR ?= ../badgeware-simulator
BUILD_DIR := build
SIM_ROOT := $(abspath $(BUILD_DIR)/simulator-root)
APP_FILES := __init__.py avatar.png rocket.png social-qr.png

.PHONY: help sim deploy firmware _check

help:
	@printf '%s\n' \
		'Badger commands:' \
		'  make sim       Run the app in Badgeware Desktop' \
		'  make deploy    Copy the app to a Badger in disk mode' \
		'  make firmware  Install the latest firmware and system files'

social-qr.png: tools/generate_qr.py pyproject.toml uv.lock
	$(PYTHON) tools/generate_qr.py "https://seanboult.dev" "$@"

_check:
	@command -v "$(UV)" >/dev/null 2>&1 || { \
		echo 'error: install uv from https://docs.astral.sh/uv/' >&2; exit 1; \
	}
	@$(PYTHON) tools/check_app.py $(APP_FILES)
	@$(UV) run ruff check .

sim: social-qr.png _check
	@if test ! -d "$(SIM_DIR)"; then \
		git clone --recurse-submodules https://github.com/pimoroni/badgeware-simulator.git "$(SIM_DIR)"; \
	fi
	@$(PYTHON) tools/patch_simulator.py "$(SIM_DIR)"
	@if test ! -x "$(SIM_DIR)/build/micropython" || \
	   test "$(SIM_DIR)/micropython/main.c" -nt "$(SIM_DIR)/build/micropython"; then \
		$(MAKE) -C "$(SIM_DIR)" -j; \
	else \
		echo "Using existing simulator build at $(SIM_DIR)/build/micropython"; \
	fi
	@mkdir -p "$(SIM_ROOT)"
	@rsync -a --delete "$(SIM_DIR)/root-badgeware/" "$(SIM_ROOT)/"
	@mkdir -p "$(SIM_ROOT)/system/apps/badge"
	@rsync -a --checksum $(APP_FILES) "$(SIM_ROOT)/system/apps/badge/"
	@rsync -a simulator/main.py "$(SIM_ROOT)/main.py"
	@cd "$(SIM_DIR)" && ./build/micropython root="$(SIM_ROOT)" watch="$(SIM_ROOT)/system"

deploy: social-qr.png _check
	@test -n "$(BADGER_MOUNT)" && test -d "$(BADGER_MOUNT)/apps" || { \
		echo 'error: Badger drive not found; double-tap RESET and try again.' >&2; exit 1; \
	}
	@mkdir -p "$(BADGER_MOUNT)/apps/badge"
	@rsync -av --checksum $(APP_FILES) "$(BADGER_MOUNT)/apps/badge/"
	@sync
	@if command -v diskutil >/dev/null 2>&1; then \
		diskutil eject "$(BADGER_MOUNT)"; \
	else \
		echo "Safely eject $(BADGER_MOUNT) to reboot the badge."; \
	fi

firmware:
	@command -v "$(UV)" >/dev/null 2>&1 || { \
		echo 'error: install uv from https://docs.astral.sh/uv/' >&2; exit 1; \
	}
	@test -n "$(BOOT_MOUNT)" && test -d "$(BOOT_MOUNT)" || { \
		echo 'error: RP2350 drive not found; hold BOOT, tap RESET, then release BOOT.' >&2; exit 1; \
	}
	@$(PYTHON) tools/firmware.py flash --with-filesystem --mount "$(BOOT_MOUNT)" --output-dir "$(BUILD_DIR)"
