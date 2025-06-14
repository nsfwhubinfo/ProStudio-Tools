#!/usr/bin/env python3
"""Test ProStudio components availability"""

import json
import os
import sys

def test_components():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        print("Error: config.json not found")
        return False
    
    with open(config_path) as f:
        config = json.load(f)
    
    print("ProStudio Component Status:")
    print("-" * 30)
    
    all_ready = True
    for component, info in config['components'].items():
        status = info['status']
        if status == 'ready':
            print(f"✓ {component}: {status}")
        else:
            print(f"✗ {component}: {status}")
            all_ready = False
    
    print("\nPaths Configuration:")
    print(f"Base: {config['base_path']}")
    print(f"Models: {config['models_path']}")
    print(f"Outputs: {config['output_path']}")
    
    return all_ready

if __name__ == "__main__":
    sys.exit(0 if test_components() else 1)
