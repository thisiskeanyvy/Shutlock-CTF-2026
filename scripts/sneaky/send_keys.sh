#!/bin/sh
PASS="$1"
MODE="$2"

# Check arg count
if [ $# -lt 1 ]; then
    echo "[ERROR] Script must have at least 1 argument"
    printf "Usage:./scripts/send_keys <password> [-d]\n\tpassword: kernel decryption password\n\t-d: (optional) run in debug mode"
    exit
fi

printf "${PASS}\r" | ./scripts/run_kernel.sh "$MODE" 
