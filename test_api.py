#!/usr/bin/env python3
"""Test the ProStudio API"""

import requests
import json

# Test health endpoint
print("Testing health endpoint...")
response = requests.get("http://localhost/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test generation endpoint
print("\nTesting generation endpoint...")
data = {
    "concept": "Zero Cost Deployment Success",
    "platform": "tiktok",
    "style": "creative"
}

response = requests.post("http://localhost/api/generate", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# List all endpoints
print("\nTesting root endpoint...")
response = requests.get("http://localhost/")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")