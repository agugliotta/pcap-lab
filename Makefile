.PHONY: install generate replay test clean help

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
CLI := $(PYTHON) main.py

install:
	@if [ ! -d "$(VENV)" ]; then python3 -m venv $(VENV); fi
	$(PIP) install -r requirements.txt

generate:
	sudo $(CLI) generate $(STUDENT) $(INTERFACE)

replay:
	@# tcpreplay usually needs sudo. Optional TARGET_IP and TARGET_PORT can be provided.
	sudo $(CLI) replay $(INTERFACE) $(FILE) $(if $(TARGET_IP),--target-ip $(TARGET_IP)) $(if $(TARGET_PORT),--target-port $(TARGET_PORT))

test:
	$(CLI) test

clean:
	sudo $(CLI) clean

help:
	@$(CLI) --help
