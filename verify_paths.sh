#!/bin/bash
echo "Verifying ProStudio paths..."
echo "Base directory: /home/golde/prostudio"
[ -d "/home/golde/prostudio" ] && echo "✓ Base directory exists" || echo "✗ Base directory missing"
[ -d "/home/golde/prostudio/models" ] && echo "✓ Models directory exists" || echo "✗ Models directory missing"
[ -d "/home/golde/prostudio/outputs" ] && echo "✓ Outputs directory exists" || echo "✗ Outputs directory missing"
[ -f "/home/golde/prostudio/config.json" ] && echo "✓ Config file exists" || echo "✗ Config file missing"
