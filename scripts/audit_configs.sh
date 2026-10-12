#!/bin/bash
set -e

echo "🔍 Running Cisco VoIP Configuration Audit..."
python3 tools/cli.py audit
