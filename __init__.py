#!/usr/bin/env python3
"""
ProStudio SDK
=============

AI-Powered Content Studio for Social Media Monetization

Leverages META-CHRONOSONIC-FA-CMS integration to create viral content
while demonstrating its own capabilities through self-marketing.

Version: 1.0.0
Copyright: Tenxsom AI
"""

__version__ = "1.0.0"
__author__ = "Tenxsom AI"

# Core modules
from .core.content_engine import ContentEngine
from .core.monetization import MonetizationFramework

__all__ = [
    "ContentEngine",
    "MonetizationFramework",
    "__version__"
]