#!/bin/bash
set -e

# Arguments
STUDENT_ID=$1
INTERFACE=$2

if [ -z "$STUDENT_ID" ] || [ -z "$INTERFACE" ]; then
    echo "Usage: $0 <student_id> <interface>"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set PYTHONPATH to include the project root
export PYTHONPATH=$PROJECT_ROOT

# Run the python generator
if [ -d "$PROJECT_ROOT/.venv" ]; then
    # Use absolute path for sudo reliability
    "$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/generator/generate_pcap.py" "$STUDENT_ID" "$INTERFACE"
else
    python3 "$PROJECT_ROOT/generator/generate_pcap.py" "$STUDENT_ID" "$INTERFACE"
fi
