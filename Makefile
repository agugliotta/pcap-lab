.PHONY: install generate replay test clean

# Default shell
SHELL := /bin/bash

# Default interface - adjust as needed (e.g., lo0 for macOS, lo for Linux)
INTERFACE ?= $(shell if [ "$$(uname)" == "Darwin" ]; then echo "lo0"; else echo "lo"; fi)
STUDENT ?= test_student
FILE ?= output/$(STUDENT)/traffic.pcap

install:
	pip install -r requirements.txt

generate:
	@echo "Generating traffic for student: $(STUDENT) on interface: $(INTERFACE)"
	@# We need sudo for tcpdump
	@sudo ./scripts/generate.sh $(STUDENT) $(INTERFACE)

replay:
	@echo "Replaying traffic from: $(FILE) to interface: $(INTERFACE)"
	@sudo ./scripts/replay.sh $(INTERFACE) $(FILE)

test:
	pytest tests/

clean:
	rm -rf output/*
