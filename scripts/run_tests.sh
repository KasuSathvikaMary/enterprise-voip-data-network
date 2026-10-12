#!/bin/bash
set -e

echo "🧪 Running Automated VoIP & QoS Test Suite..."
python3 -m pytest tests/ -v --tb=short
