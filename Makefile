.PHONY: install generate replay test clean

# Default shell
SHELL := /bin/bash

# Default interface - adjust as needed (e.g., lo0 for macOS, lo for Linux)
INTERFACE ?= $(shell if [ "$$(uname)" == "Darwin" ]; then echo "lo0"; else echo "lo"; fi)
STUDENT ?= test_student
FILE ?= output/$(STUDENT)/traffic.pcap

# Python and Virtual Environment
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

install:
	@if [ ! -d "$(VENV)" ]; then python3 -m venv $(VENV); fi
	$(PIP) install -r requirements.txt

generate:
	@echo "Generating traffic for student: $(STUDENT) on interface: $(INTERFACE)"
	@# We need sudo for tcpdump, and we use the venv python to have all dependencies
	sudo ./scripts/generate.sh $(STUDENT) $(INTERFACE)

replay:
	@echo "Replaying traffic from: $(FILE) to interface: $(INTERFACE)"
	@# tcpreplay usually needs sudo. Optional TARGET_IP and TARGET_PORT can be provided.
	sudo ./scripts/replay.sh $(INTERFACE) $(FILE) $(TARGET_IP) $(TARGET_PORT)

test:
	$(VENV)/bin/pytest tests/

clean:
	sudo rm -rf output/*
