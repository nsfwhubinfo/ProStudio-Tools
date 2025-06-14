#!/usr/bin/env python3
"""
Base Classes for Content Engine
================================

Abstract base classes used throughout the content engine.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from .content_types import ContentPiece, OptimizationMetrics


class ContentGenerator(ABC):
    """Abstract base class for content generators"""
    
    @abstractmethod
    def generate(self, concept: str, parameters: Dict[str, Any]) -> ContentPiece:
        """Generate content from concept and parameters"""
        pass
    
    @abstractmethod
    def optimize(self, content: ContentPiece) -> ContentPiece:
        """Optimize content for engagement"""
        pass


class ContentOptimizer(ABC):
    """Abstract base class for content optimizers"""
    
    @abstractmethod
    def analyze(self, content: ContentPiece) -> OptimizationMetrics:
        """Analyze content and generate metrics"""
        pass
    
    @abstractmethod
    def enhance(self, content: ContentPiece, target_metrics: OptimizationMetrics) -> ContentPiece:
        """Enhance content to meet target metrics"""
        pass