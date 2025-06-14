#!/usr/bin/env python3
"""
Engagement Optimizer
====================

Optimizes content for maximum engagement using psychological triggers,
viral patterns, and platform-specific best practices.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import random

from ..base_classes import ContentOptimizer
from ..content_types import (
    ContentPiece, ContentType, Platform, OptimizationMetrics,
    ConsciousnessParameters
)


class EngagementOptimizer(ContentOptimizer):
    """
    Optimizes content for engagement using proven psychological patterns
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.psychological_triggers = self._load_psychological_triggers()
        self.viral_patterns = self._load_viral_patterns()
        self.platform_best_practices = self._load_platform_practices()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default engagement configuration"""
        return {
            'enable_psychological_optimization': True,
            'enable_viral_patterns': True,
            'enable_emotional_journey': True,
            'target_engagement_rate': 0.8,
            'optimize_for_shares': True,
            'optimize_for_saves': True
        }
    
    def _load_psychological_triggers(self) -> Dict[str, Any]:
        """Load psychological engagement triggers"""
        return {
            "curiosity_gap": {
                "elements": ["incomplete_info", "question", "reveal_promise"],
                "engagement_boost": 1.4,
                "best_for": ["educational", "story"]
            },
            "social_proof": {
                "elements": ["numbers", "testimonials", "community"],
                "engagement_boost": 1.3,
                "best_for": ["tutorial", "review"]
            },
            "fomo": {
                "elements": ["limited_time", "exclusive", "trending"],
                "engagement_boost": 1.35,
                "best_for": ["announcement", "product"]
            },
            "transformation": {
                "elements": ["before_after", "journey", "results"],
                "engagement_boost": 1.45,
                "best_for": ["lifestyle", "educational"]
            },
            "controversy": {
                "elements": ["debate", "unpopular_opinion", "challenge_norm"],
                "engagement_boost": 1.5,
                "best_for": ["opinion", "reaction"]
            },
            "nostalgia": {
                "elements": ["throwback", "memories", "classic"],
                "engagement_boost": 1.25,
                "best_for": ["entertainment", "story"]
            }
        }
    
    def _load_viral_patterns(self) -> Dict[str, Any]:
        """Load proven viral content patterns"""
        return {
            "challenge": {
                "structure": ["introduction", "demonstration", "invitation"],
                "virality_multiplier": 2.5,
                "shareability": 0.9
            },
            "reaction": {
                "structure": ["setup", "genuine_reaction", "analysis"],
                "virality_multiplier": 1.8,
                "shareability": 0.7
            },
            "educational_surprise": {
                "structure": ["common_belief", "contradiction", "proof"],
                "virality_multiplier": 2.0,
                "shareability": 0.85
            },
            "emotional_story": {
                "structure": ["relatable_start", "conflict", "resolution"],
                "virality_multiplier": 2.2,
                "shareability": 0.8
            },
            "humor": {
                "structure": ["setup", "misdirection", "punchline"],
                "virality_multiplier": 2.8,
                "shareability": 0.95
            }
        }
    
    def _load_platform_practices(self) -> Dict[str, Any]:
        """Load platform-specific best practices"""
        return {
            Platform.TIKTOK: {
                "optimal_duration": 15-30,
                "key_metrics": ["completion_rate", "shares", "comments"],
                "best_times": [6, 10, 19, 22],  # Hours in EST
                "engagement_elements": ["duet", "stitch", "sound"]
            },
            Platform.INSTAGRAM: {
                "optimal_duration": 30-60,  # For reels
                "key_metrics": ["saves", "shares", "comments"],
                "best_times": [11, 14, 17, 20],
                "engagement_elements": ["carousel", "poll", "question"]
            },
            Platform.YOUTUBE: {
                "optimal_duration": 600,  # 10 minutes
                "key_metrics": ["watch_time", "ctr", "comments"],
                "best_times": [12, 15, 20, 21],
                "engagement_elements": ["cards", "end_screen", "chapters"]
            }
        }
    
    def analyze(self, content: ContentPiece) -> OptimizationMetrics:
        """Analyze content engagement potential"""
        metrics = OptimizationMetrics()
        
        # Base engagement from content type
        base_engagement = self._calculate_base_engagement(content)
        
        # Apply psychological factors
        if self.config['enable_psychological_optimization']:
            psych_multiplier = self._analyze_psychological_factors(content)
            base_engagement *= psych_multiplier
        
        # Apply viral pattern analysis
        if self.config['enable_viral_patterns']:
            viral_score = self._analyze_viral_potential(content)
            metrics.viral_coefficient = viral_score
        
        # Platform-specific adjustments
        platform_score = self._analyze_platform_fit(content)
        
        # Calculate final metrics
        metrics.predicted_engagement = min(base_engagement * platform_score, 95)
        metrics.roi_estimate = metrics.predicted_engagement * metrics.viral_coefficient * 10
        metrics.platform_optimization_score = platform_score
        
        # Target audience analysis
        metrics.target_audience_match = self._analyze_audience_match(content)
        
        # Trend alignment
        metrics.trend_alignment = self._analyze_trend_alignment(content)
        
        return metrics
    
    def enhance(self, content: ContentPiece, target_metrics: OptimizationMetrics) -> ContentPiece:
        """Enhance content for maximum engagement"""
        # Apply psychological triggers
        if self.config['enable_psychological_optimization']:
            content = self._apply_psychological_triggers(content, target_metrics)
        
        # Enhance viral elements
        if self.config['enable_viral_patterns']:
            content = self._enhance_viral_elements(content)
        
        # Optimize for platform
        content = self._optimize_for_platform(content)
        
        # Enhance emotional journey
        if self.config['enable_emotional_journey']:
            content = self._enhance_emotional_journey(content)
        
        # Optimize timing elements
        content = self._optimize_timing(content)
        
        return content
    
    def _calculate_base_engagement(self, content: ContentPiece) -> float:
        """Calculate base engagement rate"""
        # Content type base rates
        base_rates = {
            ContentType.VIDEO_SHORT: 75,
            ContentType.VIDEO_LONG: 65,
            ContentType.IMAGE_POST: 70,
            ContentType.IMAGE_STORY: 60,
            ContentType.TEXT_POST: 55,
            ContentType.CAROUSEL: 80
        }
        
        base = base_rates.get(content.content_type, 60)
        
        # Consciousness boost
        consciousness_factor = (
            content.consciousness.coherence_level * 0.4 +
            content.consciousness.phi_resonance * 0.3 +
            min(content.consciousness.fractal_dimension / 1.618, 1.0) * 0.3
        )
        
        return base * (1 + consciousness_factor * 0.3)
    
    def _analyze_psychological_factors(self, content: ContentPiece) -> float:
        """Analyze psychological engagement factors"""
        multiplier = 1.0
        
        # Check for psychological triggers in content
        if hasattr(content, 'raw_content') and content.raw_content:
            # Look for curiosity gap
            if any(word in str(content.raw_content).lower() 
                  for word in ['secret', 'revealed', 'truth', 'nobody knows']):
                multiplier *= self.psychological_triggers['curiosity_gap']['engagement_boost']
            
            # Look for transformation
            if any(word in str(content.raw_content).lower()
                  for word in ['before', 'after', 'transformation', 'journey']):
                multiplier *= self.psychological_triggers['transformation']['engagement_boost']
        
        # Emotional spectrum analysis
        if content.consciousness.emotional_spectrum:
            high_engagement_emotions = ['curiosity', 'surprise', 'joy', 'awe']
            emotion_score = sum(
                content.consciousness.emotional_spectrum.get(emotion, 0)
                for emotion in high_engagement_emotions
            ) / len(high_engagement_emotions)
            multiplier *= (1 + emotion_score * 0.2)
        
        return multiplier
    
    def _analyze_viral_potential(self, content: ContentPiece) -> float:
        """Analyze viral potential of content"""
        viral_score = 1.0
        
        # Check for viral pattern elements
        if hasattr(content, 'raw_content') and content.raw_content:
            content_str = str(content.raw_content).lower()
            
            # Challenge pattern
            if 'challenge' in content_str:
                viral_score *= self.viral_patterns['challenge']['virality_multiplier']
            
            # Educational surprise
            elif any(word in content_str for word in ['myth', 'wrong', 'actually']):
                viral_score *= self.viral_patterns['educational_surprise']['virality_multiplier']
            
            # Humor
            elif any(word in content_str for word in ['funny', 'lol', 'joke']):
                viral_score *= self.viral_patterns['humor']['virality_multiplier']
        
        # Platform virality factors
        platform_multipliers = {
            Platform.TIKTOK: 1.3,
            Platform.INSTAGRAM: 1.1,
            Platform.YOUTUBE: 1.0
        }
        
        viral_score *= platform_multipliers.get(content.platform, 1.0)
        
        return min(viral_score, 3.0)  # Cap at 3x
    
    def _analyze_platform_fit(self, content: ContentPiece) -> float:
        """Analyze how well content fits platform"""
        if content.platform not in self.platform_best_practices:
            return 0.8
        
        practices = self.platform_best_practices[content.platform]
        fit_score = 1.0
        
        # Duration fit (for video content)
        if content.content_type in [ContentType.VIDEO_SHORT, ContentType.VIDEO_LONG]:
            if hasattr(content, 'raw_content') and 'duration' in content.raw_content:
                duration = content.raw_content['duration']
                optimal = practices['optimal_duration']
                
                if isinstance(optimal, tuple):
                    if optimal[0] <= duration <= optimal[1]:
                        fit_score *= 1.2
                elif abs(duration - optimal) < 60:
                    fit_score *= 1.1
        
        # Hashtag optimization
        if len(content.metadata.hashtags) > 5:
            fit_score *= 1.1
        
        return fit_score
    
    def _analyze_audience_match(self, content: ContentPiece) -> float:
        """Analyze target audience match"""
        # Simplified audience matching
        match_score = 0.7  # Base score
        
        # Check for audience indicators
        if content.metadata.tags:
            audience_tags = ['beginner', 'advanced', 'professional', 'teen', 'adult']
            if any(tag in content.metadata.tags for tag in audience_tags):
                match_score += 0.2
        
        # Platform audience alignment
        if content.platform == Platform.TIKTOK and content.content_type == ContentType.VIDEO_SHORT:
            match_score += 0.1  # TikTok loves short videos
        elif content.platform == Platform.YOUTUBE and content.content_type == ContentType.VIDEO_LONG:
            match_score += 0.1  # YouTube favors longer content
        
        return min(match_score, 1.0)
    
    def _analyze_trend_alignment(self, content: ContentPiece) -> float:
        """Analyze alignment with current trends"""
        trend_score = 0.5  # Base score
        
        # Check for trending keywords
        trending_keywords = [
            'ai', 'viral', '2024', '2025', 'trend', 'challenge',
            'transformation', 'routine', 'hack', 'tips'
        ]
        
        content_text = f"{content.metadata.title} {content.metadata.description}".lower()
        keyword_matches = sum(1 for keyword in trending_keywords if keyword in content_text)
        
        trend_score += min(keyword_matches * 0.1, 0.4)
        
        # Seasonal trends
        current_month = datetime.now().month
        seasonal_keywords = {
            1: ['new year', 'resolution', 'fresh start'],
            2: ['valentine', 'love'],
            10: ['halloween', 'spooky'],
            12: ['christmas', 'holiday', 'gift']
        }
        
        if current_month in seasonal_keywords:
            if any(keyword in content_text for keyword in seasonal_keywords[current_month]):
                trend_score += 0.2
        
        return min(trend_score, 1.0)
    
    def _apply_psychological_triggers(self, 
                                    content: ContentPiece,
                                    target_metrics: OptimizationMetrics) -> ContentPiece:
        """Apply psychological triggers to content"""
        # Select best trigger based on content
        best_trigger = self._select_best_trigger(content)
        
        if best_trigger and hasattr(content, 'raw_content') and content.raw_content:
            trigger_data = self.psychological_triggers[best_trigger]
            
            # Apply trigger elements
            if 'script' in content.raw_content:
                # Enhance hook with trigger
                if best_trigger == 'curiosity_gap':
                    content.raw_content['script']['hook'] = f"The secret about {content.metadata.title} that nobody tells you..."
                elif best_trigger == 'transformation':
                    content.raw_content['script']['hook'] = f"How I transformed my {content.metadata.title} in just 30 days"
            
            # Boost predicted engagement
            content.optimization.predicted_engagement *= trigger_data['engagement_boost']
        
        return content
    
    def _select_best_trigger(self, content: ContentPiece) -> Optional[str]:
        """Select best psychological trigger for content"""
        content_text = str(content.metadata.title).lower()
        
        # Match content to triggers
        for trigger, data in self.psychological_triggers.items():
            if any(keyword in content_text for keyword in data.get('best_for', [])):
                return trigger
        
        # Default to curiosity gap
        return 'curiosity_gap'
    
    def _enhance_viral_elements(self, content: ContentPiece) -> ContentPiece:
        """Enhance viral elements in content"""
        # Add shareability factors
        if self.config['optimize_for_shares']:
            # Add share prompt
            if hasattr(content, 'raw_content') and 'script' in content.raw_content:
                content.raw_content['script']['share_prompt'] = "Tag someone who needs to see this!"
            
            # Increase viral coefficient
            content.optimization.viral_coefficient *= 1.2
        
        # Add save triggers
        if self.config['optimize_for_saves']:
            content.metadata.description += "\n💾 Save this for later!"
            content.optimization.predicted_engagement *= 1.1
        
        return content
    
    def _optimize_for_platform(self, content: ContentPiece) -> ContentPiece:
        """Optimize content for specific platform"""
        if content.platform not in self.platform_best_practices:
            return content
        
        practices = self.platform_best_practices[content.platform]
        
        # Add platform-specific elements
        if 'engagement_elements' in practices:
            elements = practices['engagement_elements']
            
            if content.platform == Platform.TIKTOK and 'duet' in elements:
                content.metadata.tags.append('duet_this')
            elif content.platform == Platform.INSTAGRAM and 'poll' in elements:
                content.metadata.tags.append('poll_in_story')
            elif content.platform == Platform.YOUTUBE and 'chapters' in elements:
                content.metadata.tags.append('has_chapters')
        
        # Optimize posting time
        best_hour = random.choice(practices.get('best_times', [12]))
        content.metadata.publish_time = datetime.now().replace(
            hour=best_hour, minute=0, second=0
        )
        
        return content
    
    def _enhance_emotional_journey(self, content: ContentPiece) -> ContentPiece:
        """Enhance emotional journey for engagement"""
        # Create emotional arc
        emotional_arc = [
            ('curiosity', 0.8),
            ('anticipation', 0.9),
            ('surprise', 1.0),
            ('satisfaction', 0.85),
            ('inspiration', 0.9)
        ]
        
        # Map to content structure
        if hasattr(content, 'raw_content') and 'structure' in content.raw_content:
            if 'emotional_journey' not in content.raw_content:
                content.raw_content['emotional_journey'] = []
            
            chapters = content.raw_content['structure'].get('chapters', [])
            for i, (chapter, (emotion, intensity)) in enumerate(zip(chapters, emotional_arc)):
                if i < len(emotional_arc):
                    chapter['target_emotion'] = emotion
                    chapter['emotional_intensity'] = intensity
        
        # Update consciousness emotional spectrum
        content.consciousness.emotional_spectrum = {
            emotion: intensity
            for emotion, intensity in emotional_arc
        }
        
        return content
    
    def _optimize_timing(self, content: ContentPiece) -> ContentPiece:
        """Optimize content timing elements"""
        if hasattr(content, 'raw_content'):
            # Optimize hook timing (first 3 seconds crucial)
            if 'structure' in content.raw_content:
                structure = content.raw_content['structure']
                
                # Ensure strong hook
                if 'hooks' not in structure:
                    structure['hooks'] = []
                
                # Add hook at 0 seconds if not present
                if not any(h.get('time', -1) == 0 for h in structure['hooks']):
                    structure['hooks'].insert(0, {
                        'time': 0,
                        'type': 'attention_grab',
                        'intensity': 1.0
                    })
                
                # Add retention hook every 30 seconds
                duration = structure.get('total_duration', 60)
                for t in range(30, int(duration), 30):
                    if not any(abs(h.get('time', -1) - t) < 5 for h in structure['hooks']):
                        structure['hooks'].append({
                            'time': t,
                            'type': 'retention',
                            'intensity': 0.8
                        })
        
        return content


def demo_engagement_optimizer():
    """Demonstrate engagement optimization"""
    print("ENGAGEMENT OPTIMIZER DEMO")
    print("=" * 60)
    
    optimizer = EngagementOptimizer()
    
    # Create test content
    from ..content_types import ContentPiece, ContentType, Platform, ContentMetadata
    
    test_cases = [
        ("The Secret to Going Viral Nobody Tells You", Platform.TIKTOK),
        ("My 30-Day AI Transformation", Platform.INSTAGRAM),
        ("Why Everything You Know About Content is Wrong", Platform.YOUTUBE)
    ]
    
    for title, platform in test_cases:
        print(f"\n{'='*50}")
        print(f"Content: {title}")
        print(f"Platform: {platform.value}")
        print(f"{'='*50}")
        
        # Create content
        content = ContentPiece(
            content_type=ContentType.VIDEO_SHORT,
            platform=platform,
            metadata=ContentMetadata(
                title=title,
                description=f"Discover {title.lower()}",
                tags=['viral', 'content', 'creator']
            )
        )
        
        # Set consciousness parameters
        content.consciousness.coherence_level = 0.8
        content.consciousness.phi_resonance = 0.618
        
        # Add raw content for testing
        content.raw_content = {
            'duration': 30,
            'script': {'hook': f"Wait until you hear about {title}"},
            'structure': {'chapters': [{'name': 'hook'}, {'name': 'content'}, {'name': 'cta'}]}
        }
        
        # Analyze
        print("\n📊 Initial Analysis:")
        metrics = optimizer.analyze(content)
        print(f"  Predicted Engagement: {metrics.predicted_engagement:.1f}%")
        print(f"  Viral Coefficient: {metrics.viral_coefficient:.2f}")
        print(f"  Audience Match: {metrics.target_audience_match:.1%}")
        print(f"  Trend Alignment: {metrics.trend_alignment:.1%}")
        
        # Enhance
        print("\n🚀 After Enhancement:")
        enhanced = optimizer.enhance(content, metrics)
        enhanced_metrics = optimizer.analyze(enhanced)
        
        print(f"  Predicted Engagement: {enhanced_metrics.predicted_engagement:.1f}% (+{enhanced_metrics.predicted_engagement - metrics.predicted_engagement:.1f}%)")
        print(f"  Viral Coefficient: {enhanced_metrics.viral_coefficient:.2f} (+{enhanced_metrics.viral_coefficient - metrics.viral_coefficient:.2f})")
        
        # Show enhancements
        if hasattr(enhanced, 'raw_content'):
            if 'share_prompt' in enhanced.raw_content.get('script', {}):
                print(f"  Added: Share prompt")
            if 'emotional_journey' in enhanced.raw_content:
                print(f"  Added: Emotional journey")
            if enhanced.metadata.publish_time:
                print(f"  Optimal publish time: {enhanced.metadata.publish_time.strftime('%I %p')}")
    
    print("\n✅ Engagement optimizer demo complete!")


if __name__ == "__main__":
    demo_engagement_optimizer()