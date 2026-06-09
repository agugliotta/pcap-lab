#!/bin/bash

# Arguments
INTERFACE=$1
PCAP_FILE=$2
TARGET_IP=$3    # Optional
TARGET_PORT=$4  # Optional

if [ -z "$INTERFACE" ] || [ -z "$PCAP_FILE" ]; then
    echo "Usage: $0 <interface> <pcap_file> [target_ip] [target_port]"
    echo "Example: $0 eth0 output/student1/traffic.pcap 192.168.1.10 80"
    exit 1
fi

if ! command -v tcpreplay &> /dev/null; then
    echo "Error: tcpreplay is not installed."
    echo "Install it via: sudo apt install tcpreplay (Linux) or brew install tcpreplay (macOS)"
    exit 1
fi

REPLAY_FILE="$PCAP_FILE"

# If IP or Port is provided, we need to rewrite the PCAP
if [ -n "$TARGET_IP" ] || [ -n "$TARGET_PORT" ]; then
    REWRITE_CMD="tcprewrite --infile=\"$PCAP_FILE\" --outfile=\"$PCAP_FILE.tmp\""
    
    # Rewrite Destination IP (Default in PCAP is 127.0.0.1)
    if [ -n "$TARGET_IP" ]; then
        echo "Rewriting destination IP to $TARGET_IP..."
        REWRITE_CMD="$REWRITE_CMD --dstipmap=127.0.0.1/32:$TARGET_IP/32"
    fi
    
    # Rewrite Port (Default in PCAP is 8080)
    if [ -n "$TARGET_PORT" ]; then
        echo "Rewriting destination port to $TARGET_PORT..."
        REWRITE_CMD="$REWRITE_CMD --portmap=8080:$TARGET_PORT"
    fi
    
    # Execute rewrite
    eval "$REWRITE_CMD --fixcsum"
    REPLAY_FILE="$PCAP_FILE.tmp"
fi

echo "Replaying $REPLAY_FILE on $INTERFACE..."
tcpreplay --intf1="$INTERFACE" --topspeed "$REPLAY_FILE"

# Clean up temporary file if it was created
if [ "$REPLAY_FILE" != "$PCAP_FILE" ]; then
    rm "$REPLAY_FILE"
fi
