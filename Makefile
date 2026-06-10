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
	sudo $(CLI) replay $(INTERFACE) $(FILE)

test:
	$(CLI) test

clean:
	sudo $(CLI) clean

help:
	@$(CLI) --help
