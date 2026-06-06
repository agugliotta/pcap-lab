#!/bin/bash

# Arguments
INTERFACE=$1
PCAP_FILE=$2

if [ -z "$INTERFACE" ] || [ -z "$PCAP_FILE" ]; then
    echo "Usage: $0 <interface> <pcap_file>"
    echo "Example: $0 eth0 output/student1/traffic.pcap"
    exit 1
fi

if ! command -v tcpreplay &> /dev/null; then
    echo "Error: tcpreplay is not installed."
    echo "Install it via: sudo apt install tcpreplay (Linux) or brew install tcpreplay (macOS)"
    exit 1
fi

echo "Replaying $PCAP_FILE on $INTERFACE..."
tcpreplay --intf1="$INTERFACE" --topspeed "$PCAP_FILE"
