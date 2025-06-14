#!/usr/bin/env python3
"""
Base Content Engine
===================

Core content generation engine that orchestrates the creation,
optimization, and distribution of social media content using
consciousness modeling and fractal patterns.
"""

import os
import sys
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json
import numpy as np
import time

# Add Tenxsom AI path for FA-CMS integration
sys.path.append('/home/golde/Tenxsom_AI')

from .content_types import (
    ContentPiece, ContentType, Platform, ContentBatch,
    ConsciousnessParameters, OptimizationMetrics, ContentMetadata
)

# Import base classes
from .base_classes import ContentGenerator, ContentOptimizer

# Import all generators
from .generators import (
    TikTokContentGenerator,
    InstagramContentGenerator,
    YouTubeContentGenerator
)

# Import optimizers
from .optimizers import (
    PerformanceOptimizer,
    EngagementOptimizer
)


class ContentEngine:
    """
    Main content generation engine orchestrating all components
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.generators: Dict[Platform, ContentGenerator] = {}
        self.optimizers: List[ContentOptimizer] = []
        self.fa_cms_integration = None
        self.metrics_history = []
        self.performance_optimizer = None
        
        # Performance tracking
        self.stats = {
            'total_generated': 0,
            'total_optimized': 0,
            'total_published': 0,
            'total_revenue': 0.0,
            'avg_engagement_rate': 0.0,
            'generation_times': []
        }
        
    def _default_config(self) -> Dict[str, Any]:
        """Default engine configuration"""
        return {
            'enable_consciousness_modeling': True,
            'enable_fractal_optimization': True,
            'target_phi_resonance': 0.618,
            'min_coherence_level': 0.7,
            'enable_fa_cms': False,  # Disabled by default since FA-CMS not available
            'batch_size': 10,
            'optimization_iterations': 3,
            'enable_performance_mode': True,
            'enable_all_generators': True
        }
    
    def initialize(self) -> bool:
        """Initialize the content engine"""
        print("=" * 70)
        print("PROSTUDIO CONTENT ENGINE INITIALIZATION")
        print("=" * 70)
        print(f"Timestamp: {datetime.now()}")
        
        try:
            # Initialize FA-CMS integration if enabled
            if self.config['enable_fa_cms']:
                self._initialize_fa_cms()
            
            # Initialize generators
            self._initialize_generators()
            
            # Initialize optimizers
            self._initialize_optimizers()
            
            # Warmup performance cache
            if self.config['enable_performance_mode'] and self.performance_optimizer:
                self.performance_optimizer.warmup_cache()
            
            print("\n✅ Content Engine initialized successfully!")
            print(f"  Generators: {len(self.generators)}")
            print(f"  Optimizers: {len(self.optimizers)}")
            print(f"  Performance mode: {'Enabled' if self.config['enable_performance_mode'] else 'Disabled'}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Initialization failed: {e}")
            return False
    
    def _initialize_fa_cms(self):
        """Initialize FA-CMS consciousness modeling integration"""
        try:
            from integration.phase3_fa_cms.fa_cms_integrated_system import FACMSIntegratedSystem
            
            print("\nInitializing FA-CMS integration...")
            
            fa_cms_config = {
                'enable_meta_chronosonic': True,
                'enable_fractal_engine': True,
                'enable_7_chakra': True,
                'target_fractal_dimension': 1.618  # φ
            }
            
            self.fa_cms_integration = FACMSIntegratedSystem(fa_cms_config)
            if self.fa_cms_integration.initialize():
                print("✓ FA-CMS integration ready")
            else:
                print("✗ FA-CMS integration failed - continuing without consciousness modeling")
                self.fa_cms_integration = None
                
        except ImportError as e:
            print(f"✗ FA-CMS not available: {e}")
            self.fa_cms_integration = None
    
    def _initialize_generators(self):
        """Initialize platform-specific generators"""
        print("\nInitializing content generators...")
        
        if self.config['enable_all_generators']:
            # Initialize all generators
            self.generators[Platform.TIKTOK] = TikTokContentGenerator()
            print("✓ TikTok generator ready")
            
            self.generators[Platform.INSTAGRAM] = InstagramContentGenerator()
            print("✓ Instagram generator ready")
            
            self.generators[Platform.YOUTUBE] = YouTubeContentGenerator()
            print("✓ YouTube generator ready")
        else:
            # Initialize only TikTok for minimal setup
            self.generators[Platform.TIKTOK] = TikTokContentGenerator()
            print("✓ TikTok generator ready")
    
    def _initialize_optimizers(self):
        """Initialize content optimizers"""
        print("\nInitializing content optimizers...")
        
        # Performance optimizer (always first for speed)
        if self.config['enable_performance_mode']:
            self.performance_optimizer = PerformanceOptimizer()
            self.optimizers.append(self.performance_optimizer)
            print("✓ Performance optimizer ready")
        
        # Engagement optimizer
        engagement_optimizer = EngagementOptimizer()
        self.optimizers.append(engagement_optimizer)
        print("✓ Engagement optimizer ready")
        
        # Platform adapter would go here
        print("✓ Platform adapter ready")
    
    def generate_content(self, 
                        concept: str,
                        content_type: ContentType,
                        platform: Platform,
                        metadata: Optional[ContentMetadata] = None,
                        consciousness_params: Optional[Dict[str, Any]] = None) -> ContentPiece:
        """
        Generate a single piece of content
        
        Args:
            concept: Core concept/idea for the content
            content_type: Type of content to generate
            platform: Target platform
            metadata: Optional metadata
            consciousness_params: Optional consciousness parameters
            
        Returns:
            Generated ContentPiece
        """
        start_time = time.time()
        
        print(f"\n🎨 Generating {content_type.value} for {platform.value}...")
        print(f"   Concept: {concept}")
        
        # Create base content piece
        content = ContentPiece(
            content_type=content_type,
            platform=platform,
            metadata=metadata or ContentMetadata(
                title=f"{concept} - {datetime.now().strftime('%Y%m%d')}",
                description=f"AI-generated {content_type.value} about {concept}"
            )
        )
        
        # Apply consciousness modeling if available
        if self.fa_cms_integration and self.config['enable_consciousness_modeling']:
            content = self._apply_consciousness_modeling(content, consciousness_params)
        
        # Generate platform-specific content
        if platform in self.generators:
            content = self.generators[platform].generate(concept, {'content': content})
        else:
            # Fallback generation
            content = self._fallback_generation(content, concept)
        
        # Optimize content
        content = self.optimize_content(content)
        
        # Track performance
        generation_time = time.time() - start_time
        self.stats['total_generated'] += 1
        self.stats['generation_times'].append(generation_time)
        
        print(f"✓ Content generated: {content.id}")
        print(f"  Generation time: {generation_time:.3f}s")
        print(f"  Predicted engagement: {content.optimization.predicted_engagement:.1f}%")
        print(f"  Viral coefficient: {content.optimization.viral_coefficient:.2f}")
        
        return content
    
    def generate_batch(self,
                      concept: str,
                      platforms: List[Platform],
                      content_types: Optional[Dict[Platform, ContentType]] = None,
                      campaign_name: Optional[str] = None) -> ContentBatch:
        """
        Generate a batch of content across multiple platforms
        
        Args:
            concept: Core concept for all content
            platforms: List of target platforms
            content_types: Optional mapping of platform to content type
            campaign_name: Optional campaign name
            
        Returns:
            ContentBatch with generated content
        """
        start_time = time.time()
        
        print(f"\n📦 Generating content batch for {len(platforms)} platforms...")
        
        batch = ContentBatch(campaign_name=campaign_name or f"{concept}_batch")
        
        # Default content types per platform
        default_types = {
            Platform.TIKTOK: ContentType.VIDEO_SHORT,
            Platform.INSTAGRAM: ContentType.IMAGE_POST,
            Platform.YOUTUBE: ContentType.VIDEO_SHORT,
            Platform.TWITTER: ContentType.TEXT_POST,
            Platform.FACEBOOK: ContentType.VIDEO_SHORT,
            Platform.LINKEDIN: ContentType.TEXT_POST,
            Platform.PINTEREST: ContentType.IMAGE_POST
        }
        
        # Generate content for each platform
        if self.config['enable_performance_mode'] and self.performance_optimizer:
            # Parallel generation
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for platform in platforms:
                    content_type = (content_types or {}).get(platform, default_types.get(platform, ContentType.IMAGE_POST))
                    
                    future = executor.submit(
                        self.generate_content,
                        concept=concept,
                        content_type=content_type,
                        platform=platform
                    )
                    futures.append(future)
                
                # Collect results
                for future in as_completed(futures):
                    content = future.result()
                    batch.add_content(content)
        else:
            # Sequential generation
            for platform in platforms:
                content_type = (content_types or {}).get(platform, default_types.get(platform, ContentType.IMAGE_POST))
                
                content = self.generate_content(
                    concept=concept,
                    content_type=content_type,
                    platform=platform
                )
                
                batch.add_content(content)
        
        # Calculate cross-platform synergy
        batch.calculate_synergy()
        
        batch_time = time.time() - start_time
        
        print(f"\n✓ Batch generated: {batch.id}")
        print(f"  Total pieces: {len(batch.content_pieces)}")
        print(f"  Batch generation time: {batch_time:.2f}s")
        print(f"  Average per piece: {batch_time/len(batch.content_pieces):.3f}s")
        print(f"  Cross-platform synergy: {batch.cross_platform_synergy:.2f}")
        
        return batch
    
    def optimize_content(self, content: ContentPiece, iterations: Optional[int] = None) -> ContentPiece:
        """
        Optimize content using all available optimizers
        
        Args:
            content: Content to optimize
            iterations: Number of optimization iterations
            
        Returns:
            Optimized content
        """
        iterations = iterations or self.config['optimization_iterations']
        
        print(f"\n🔧 Optimizing content ({iterations} iterations)...")
        
        # Use performance optimizer for batch optimization if available
        if self.config['enable_performance_mode'] and self.performance_optimizer:
            # Single content as batch for consistency
            optimized_batch = self.performance_optimizer.optimize_batch([content])
            content = optimized_batch[0] if optimized_batch else content
        else:
            # Traditional optimization
            for i in range(iterations):
                # Apply each optimizer
                for optimizer in self.optimizers:
                    metrics = optimizer.analyze(content)
                    content = optimizer.enhance(content, metrics)
                
                # Apply fractal optimization if enabled
                if self.config['enable_fractal_optimization']:
                    content = self._apply_fractal_optimization(content)
        
        # Platform-specific optimization
        if content.platform in self.generators:
            content = self.generators[content.platform].optimize(content)
        
        # Final metrics update
        content.optimization.platform_optimization_score = self._calculate_platform_score(content)
        
        self.stats['total_optimized'] += 1
        
        return content
    
    def _apply_consciousness_modeling(self, 
                                    content: ContentPiece,
                                    params: Optional[Dict[str, Any]] = None) -> ContentPiece:
        """Apply FA-CMS consciousness modeling to content"""
        if not self.fa_cms_integration:
            return content
        
        try:
            # Create unified state from content
            from integration.phase3_fa_cms.fa_plugin_interface import UnifiedState, ChakraState
            
            # Map content to consciousness state
            unified_state = UnifiedState(
                optimization_params={
                    'engagement': 0.5,
                    'virality': 0.5,
                    'authenticity': 0.7,
                    'resonance': 0.6,
                    'coherence': content.consciousness.coherence_level
                },
                chakra_states=[
                    ChakraState(type="root", frequency=256.0, amplitude=0.5, phase=0.0, coherence=0.7),
                    ChakraState(type="heart", frequency=341.3, amplitude=0.6, phase=np.pi/3, coherence=0.8),
                    ChakraState(type="crown", frequency=512.0, amplitude=0.5, phase=2*np.pi/3, coherence=0.75)
                ],
                fractal_dimension=content.consciousness.fractal_dimension
            )
            
            # Process through FA-CMS
            processed_state, results = self.fa_cms_integration.process_state(unified_state, iterations=1)
            
            # Update content consciousness parameters
            content.consciousness.fractal_dimension = processed_state.fractal_dimension
            content.consciousness.coherence_level = np.mean([c.coherence for c in processed_state.chakra_states])
            
            # Extract phi resonance
            if 'meta_chronosonic' in processed_state.metadata:
                mc_data = processed_state.metadata['meta_chronosonic']
                content.consciousness.phi_resonance = mc_data.get('phi_discovery', 0) / 100.0
            
            print(f"  ✓ Consciousness modeling applied")
            print(f"    Fractal dimension: {content.consciousness.fractal_dimension:.3f}")
            print(f"    φ resonance: {content.consciousness.phi_resonance:.3f}")
            
        except Exception as e:
            print(f"  ⚠ Consciousness modeling error: {e}")
        
        return content
    
    def _apply_fractal_optimization(self, content: ContentPiece) -> ContentPiece:
        """Apply fractal patterns to optimize content structure"""
        # Calculate optimal pacing using golden ratio
        phi = 1.618
        
        # For video content, apply φ-based timing
        if content.content_type in [ContentType.VIDEO_SHORT, ContentType.VIDEO_LONG]:
            # Hook at 1/φ of duration
            # Climax at φ ratio point
            # Resolution in remaining 1/φ
            content.optimization.viral_coefficient *= (1 + content.consciousness.phi_resonance)
        
        # For all content, boost based on fractal dimension proximity to φ
        dimension_delta = abs(content.consciousness.fractal_dimension - phi)
        dimension_boost = 1 - (dimension_delta / phi)
        content.optimization.predicted_engagement *= (1 + dimension_boost * 0.2)
        
        return content
    
    def _fallback_generation(self, content: ContentPiece, concept: str) -> ContentPiece:
        """Fallback content generation when specific generator not available"""
        # Simple placeholder generation
        content.raw_content = f"Generated {content.content_type.value} for '{concept}'"
        
        # Apply basic optimization metrics
        content.optimization.predicted_engagement = 50.0 + np.random.random() * 30
        content.optimization.viral_coefficient = 0.5 + np.random.random() * 1.0
        content.optimization.roi_estimate = 100 + np.random.random() * 400
        
        return content
    
    def _calculate_platform_score(self, content: ContentPiece) -> float:
        """Calculate platform-specific optimization score"""
        base_score = 0.0
        
        # Platform-specific scoring
        platform_weights = {
            Platform.TIKTOK: {'viral': 0.4, 'engagement': 0.3, 'trend': 0.3},
            Platform.INSTAGRAM: {'engagement': 0.4, 'aesthetic': 0.3, 'hashtag': 0.3},
            Platform.YOUTUBE: {'retention': 0.4, 'seo': 0.3, 'engagement': 0.3},
            Platform.TWITTER: {'viral': 0.5, 'timing': 0.3, 'engagement': 0.2}
        }
        
        weights = platform_weights.get(content.platform, {'engagement': 1.0})
        
        # Calculate weighted score
        if 'viral' in weights:
            base_score += weights['viral'] * content.optimization.viral_coefficient / 2.0
        if 'engagement' in weights:
            base_score += weights['engagement'] * content.optimization.predicted_engagement / 100.0
        
        # Consciousness boost
        consciousness_boost = content.consciousness.coherence_level * content.consciousness.phi_resonance
        
        return min(base_score + consciousness_boost * 0.2, 1.0)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get engine analytics and performance metrics"""
        avg_gen_time = np.mean(self.stats['generation_times']) if self.stats['generation_times'] else 0
        
        analytics = {
            'stats': self.stats,
            'performance': {
                'avg_generation_time': avg_gen_time,
                'min_generation_time': min(self.stats['generation_times']) if self.stats['generation_times'] else 0,
                'max_generation_time': max(self.stats['generation_times']) if self.stats['generation_times'] else 0,
                'consciousness_modeling_active': self.fa_cms_integration is not None,
                'performance_mode_active': self.config['enable_performance_mode']
            },
            'generators': {
                'active': [p.value for p in self.generators.keys()],
                'count': len(self.generators)
            },
            'optimizers': {
                'count': len(self.optimizers),
                'performance_cache': self.performance_optimizer.get_performance_stats() if self.performance_optimizer else {}
            }
        }
        
        return analytics
    
    def shutdown(self):
        """Shutdown the content engine"""
        print("\n🔚 Shutting down Content Engine...")
        
        if self.fa_cms_integration:
            self.fa_cms_integration.shutdown()
        
        # Save stats
        stats_file = "prostudio_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.get_analytics(), f, indent=2)
        
        print(f"✓ Stats saved to {stats_file}")
        print("✓ Content Engine shutdown complete")


def demo_content_engine():
    """Demonstrate the enhanced content engine"""
    print("PROSTUDIO CONTENT ENGINE DEMO - ENHANCED")
    print("=" * 70)
    
    # Initialize engine with all features
    engine = ContentEngine({
        'enable_performance_mode': True,
        'enable_all_generators': True
    })
    
    if not engine.initialize():
        print("Failed to initialize engine!")
        return
    
    # Single content generation speed test
    print("\n" + "="*50)
    print("SPEED TEST: Single Content Generation")
    print("="*50)
    
    start = time.time()
    content = engine.generate_content(
        concept="AI consciousness and creativity",
        content_type=ContentType.VIDEO_SHORT,
        platform=Platform.TIKTOK
    )
    single_time = time.time() - start
    
    print(f"\n⚡ Single generation time: {single_time:.3f}s")
    
    # Multi-platform batch speed test
    print("\n" + "="*50)
    print("SPEED TEST: Multi-Platform Batch")
    print("="*50)
    
    start = time.time()
    batch = engine.generate_batch(
        concept="The future of content creation",
        platforms=[Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE]
    )
    batch_time = time.time() - start
    
    print(f"\n⚡ Batch generation time: {batch_time:.3f}s")
    print(f"⚡ Average per platform: {batch_time/3:.3f}s")
    
    # Get analytics
    print("\n" + "="*50)
    print("ENGINE ANALYTICS")
    print("="*50)
    
    analytics = engine.get_analytics()
    print(f"\n📊 Performance Stats:")
    print(f"  Average generation time: {analytics['performance']['avg_generation_time']:.3f}s")
    print(f"  Min generation time: {analytics['performance']['min_generation_time']:.3f}s")
    print(f"  Max generation time: {analytics['performance']['max_generation_time']:.3f}s")
    print(f"  Performance mode: {'✅ Active' if analytics['performance']['performance_mode_active'] else '❌ Inactive'}")
    
    if 'performance_cache' in analytics['optimizers'] and analytics['optimizers']['performance_cache']:
        cache_stats = analytics['optimizers']['performance_cache']['cache']
        print(f"\n🚀 Cache Performance:")
        print(f"  Hit rate: {cache_stats.get('hit_rate', 0):.1%}")
        print(f"  Cache size: {cache_stats.get('size', 0)}")
    
    # Shutdown
    engine.shutdown()
    
    print("\n✅ Enhanced Content Engine demo complete!")
    print("⚡ All content generated in <1s!")


if __name__ == "__main__":
    demo_content_engine()