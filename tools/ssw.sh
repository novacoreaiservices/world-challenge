#!/bin/bash
# Runs sogni-agent with the SOGNI_API_KEY read at runtime from the key file.
# The key is never printed, logged, or stored. Usage: ssw.sh <sogni-agent args...>
set -euo pipefail
KEY_FILE="/home/hatch/workspace/user/files/Securesafe_0_52hx.txt"
export SOGNI_API_KEY
SOGNI_API_KEY="$(python3 -c "print(open('$KEY_FILE', encoding='utf-8-sig').read().strip().split()[0])")"
AGENT="$HOME/workspace/goals/win-the-sogni-world-builders-challenge/hidden_files/project/skill-cli/node_modules/.bin/sogni-agent"
# Route Sogni traffic through the egress proxy (this VM is outbound-only).
export NODE_OPTIONS="--import $HOME/workspace/goals/win-the-sogni-world-builders-challenge/hidden_files/project/sogni-proxy-preload.mjs ${NODE_OPTIONS:-}"
exec "$AGENT" "$@"
