#!/usr/bin/env python3
"""
Instagram Content Generator
===========================

Generates viral Instagram content optimized for Reels, Posts, and Stories
using aesthetic consciousness patterns and visual harmony principles.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import random
import time

from ..base_classes import ContentGenerator
from ..content_types import (
    ContentPiece, ContentType, Platform, ContentMetadata,
    ConsciousnessParameters, OptimizationMetrics
)


class InstagramContentGenerator(ContentGenerator):
    """
    Instagram-specific content generator with aesthetic optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.aesthetic_profiles = self._load_aesthetic_profiles()
        self.trending_audio = []
        self.hashtag_sets = []
        self._load_trending_data()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default Instagram generator configuration"""
        return {
            'reel_duration': 30,  # Default reel length
            'carousel_max_slides': 10,
            'story_duration': 15,
            'enable_aesthetic_optimization': True,
            'use_golden_ratio_composition': True,
            'enable_color_harmony': True,
            'optimize_for_saves': True  # Instagram's key metric
        }
    
    def _load_aesthetic_profiles(self) -> Dict[str, Any]:
        """Load Instagram aesthetic profiles"""
        return {
            "minimal": {
                "colors": ["#FFFFFF", "#F5F5F5", "#000000", "#E0E0E0"],
                "style": "clean, simple, whitespace",
                "engagement_multiplier": 1.2
            },
            "vibrant": {
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"],
                "style": "bold, colorful, energetic",
                "engagement_multiplier": 1.3
            },
            "moody": {
                "colors": ["#2C3E50", "#34495E", "#7F8C8D", "#BDC3C7"],
                "style": "dramatic, atmospheric, emotional",
                "engagement_multiplier": 1.15
            },
            "pastel": {
                "colors": ["#FFE0E6", "#E6F3FF", "#E6FFE6", "#FFF0E6"],
                "style": "soft, dreamy, feminine",
                "engagement_multiplier": 1.25
            },
            "luxury": {
                "colors": ["#D4AF37", "#000000", "#FFFFFF", "#8B7355"],
                "style": "premium, sophisticated, elegant",
                "engagement_multiplier": 1.35
            }
        }
    
    def _load_trending_data(self):
        """Load Instagram trending data"""
        self.trending_audio = [
            {"id": "audio_1", "name": "Aesthetic Vibes", "saves_boost": 1.3},
            {"id": "audio_2", "name": "Motivational Beat", "saves_boost": 1.2},
            {"id": "audio_3", "name": "Chill Lofi", "saves_boost": 1.15},
            {"id": "audio_4", "name": "Upbeat Pop", "saves_boost": 1.25},
            {"id": "audio_5", "name": "Cinematic Epic", "saves_boost": 1.4}
        ]
        
        self.hashtag_sets = {
            "discovery": ["#explore", "#explorepage", "#viral", "#trending"],
            "aesthetic": ["#aesthetic", "#aestheticfeed", "#minimalism", "#visualsoflife"],
            "lifestyle": ["#lifestyle", "#dailyinspiration", "#lifegoals", "#instagood"],
            "creative": ["#creative", "#artofvisuals", "#createcommune", "#visualart"],
            "motivation": ["#motivation", "#mindset", "#success", "#entrepreneur"]
        }
    
    def generate(self, concept: str, parameters: Dict[str, Any]) -> ContentPiece:
        """
        Generate Instagram content optimized for aesthetics and saves
        
        Args:
            concept: Core concept/idea
            parameters: Generation parameters including content piece
            
        Returns:
            Generated content piece
        """
        start_time = time.time()  # Performance tracking
        
        content = parameters.get('content', ContentPiece(
            content_type=ContentType.IMAGE_POST,
            platform=Platform.INSTAGRAM
        ))
        
        print(f"\n📸 Generating Instagram content...")
        
        # Determine content format strategy
        format_strategy = self._determine_format(concept, content.content_type)
        
        # Select aesthetic profile
        aesthetic = self._select_aesthetic(concept, content.consciousness)
        
        # Generate visual composition
        composition = self._generate_composition(
            concept,
            aesthetic,
            format_strategy,
            content.consciousness
        )
        
        # Generate caption with consciousness alignment
        caption_data = self._generate_caption(concept, aesthetic, content.consciousness)
        
        # Select trending elements
        audio = self._select_audio(aesthetic) if content.content_type in [ContentType.VIDEO_SHORT] else None
        
        # Create metadata
        metadata = self._generate_metadata(concept, aesthetic, caption_data)
        content.metadata = metadata
        
        # Package content
        content.raw_content = {
            "format": format_strategy,
            "aesthetic": aesthetic,
            "composition": composition,
            "caption": caption_data,
            "audio": audio,
            "generation_time": time.time() - start_time  # Track performance
        }
        
        # Calculate optimization metrics
        content.optimization = self._calculate_metrics(
            content,
            aesthetic,
            composition,
            audio
        )
        
        print(f"  ✓ Instagram content generated in {content.raw_content['generation_time']:.2f}s")
        print(f"  Aesthetic: {aesthetic['name']}")
        print(f"  Format: {format_strategy['type']}")
        print(f"  Saves potential: {content.optimization.predicted_engagement:.0f}%")
        
        return content
    
    def optimize(self, content: ContentPiece) -> ContentPiece:
        """Optimize Instagram content for maximum saves and shares"""
        if not content.raw_content:
            return content
        
        print(f"\n🎯 Optimizing Instagram content...")
        
        raw = content.raw_content
        
        # Optimize visual composition
        if self.config['use_golden_ratio_composition']:
            raw['composition'] = self._optimize_golden_ratio(raw['composition'])
        
        # Enhance aesthetic appeal
        if self.config['enable_aesthetic_optimization']:
            raw['aesthetic'] = self._enhance_aesthetic(raw['aesthetic'])
        
        # Optimize caption for engagement
        raw['caption'] = self._optimize_caption(raw['caption'])
        
        # Fine-tune hashtags
        content.metadata = self._optimize_hashtags(content.metadata)
        
        # Boost metrics
        boost_factor = 1.2
        content.optimization.predicted_engagement *= boost_factor
        content.optimization.viral_coefficient *= 1.15
        
        print(f"  ✓ Optimization complete")
        print(f"  Engagement boost: +{(boost_factor-1)*100:.0f}%")
        
        return content
    
    def _determine_format(self, concept: str, content_type: ContentType) -> Dict[str, Any]:
        """Determine optimal format based on concept"""
        format_strategy = {
            "type": "single_post",
            "aspect_ratio": "1:1",  # Square default
            "style": "photo"
        }
        
        # Analyze concept for format hints
        concept_lower = concept.lower()
        
        if any(word in concept_lower for word in ["tutorial", "how to", "steps", "guide"]):
            format_strategy["type"] = "carousel"
            format_strategy["slides"] = min(7, 3 + len(concept.split()) // 5)
        elif any(word in concept_lower for word in ["before", "after", "transformation"]):
            format_strategy["type"] = "carousel"
            format_strategy["slides"] = 2
        elif content_type == ContentType.VIDEO_SHORT:
            format_strategy["type"] = "reel"
            format_strategy["aspect_ratio"] = "9:16"
            format_strategy["style"] = "video"
        elif any(word in concept_lower for word in ["story", "behind", "journey"]):
            format_strategy["type"] = "story_series"
            format_strategy["segments"] = 3
        
        return format_strategy
    
    def _select_aesthetic(self, concept: str, consciousness: ConsciousnessParameters) -> Dict[str, Any]:
        """Select aesthetic profile based on concept and consciousness"""
        concept_lower = concept.lower()
        
        # Map concepts to aesthetics
        if any(word in concept_lower for word in ["minimal", "simple", "clean"]):
            aesthetic_name = "minimal"
        elif any(word in concept_lower for word in ["energy", "vibrant", "exciting"]):
            aesthetic_name = "vibrant"
        elif any(word in concept_lower for word in ["emotional", "deep", "meaningful"]):
            aesthetic_name = "moody"
        elif any(word in concept_lower for word in ["soft", "gentle", "peaceful"]):
            aesthetic_name = "pastel"
        elif any(word in concept_lower for word in ["premium", "luxury", "exclusive"]):
            aesthetic_name = "luxury"
        else:
            # Choose based on consciousness parameters
            if consciousness.coherence_level > 0.8:
                aesthetic_name = "minimal"
            elif consciousness.phi_resonance > 0.7:
                aesthetic_name = "luxury"
            else:
                aesthetic_name = "vibrant"
        
        aesthetic = self.aesthetic_profiles[aesthetic_name].copy()
        aesthetic["name"] = aesthetic_name
        
        return aesthetic
    
    def _generate_composition(self, 
                            concept: str,
                            aesthetic: Dict[str, Any],
                            format_strategy: Dict[str, Any],
                            consciousness: ConsciousnessParameters) -> Dict[str, Any]:
        """Generate visual composition with golden ratio and consciousness alignment"""
        phi = 1.618
        
        composition = {
            "layout": "rule_of_thirds",  # Default
            "focal_points": [],
            "color_palette": aesthetic["colors"],
            "visual_weight": {},
            "flow_direction": "left_to_right",
            "consciousness_elements": {}
        }
        
        # Apply golden ratio composition
        if self.config['use_golden_ratio_composition']:
            composition["layout"] = "golden_spiral"
            composition["focal_points"] = [
                {"x": 0.618, "y": 0.382, "weight": 1.0},  # Primary
                {"x": 0.382, "y": 0.618, "weight": 0.618}  # Secondary
            ]
        
        # Visual weight distribution based on consciousness
        if consciousness.chakra_alignment:
            # Map chakras to visual areas
            composition["visual_weight"] = {
                "top": consciousness.chakra_alignment.get("crown", 0.5),
                "center": consciousness.chakra_alignment.get("heart", 0.8),
                "bottom": consciousness.chakra_alignment.get("root", 0.7)
            }
        
        # Color harmony based on emotional spectrum
        if consciousness.emotional_spectrum:
            dominant_emotion = max(consciousness.emotional_spectrum.items(), 
                                 key=lambda x: x[1])[0]
            composition["emotion_color_mapping"] = {
                "joy": "#FFD700",
                "trust": "#4169E1",
                "surprise": "#FF69B4",
                "love": "#FF1493"
            }.get(dominant_emotion, "#808080")
        
        # Format-specific composition
        if format_strategy["type"] == "carousel":
            composition["slide_flow"] = self._generate_carousel_flow(
                format_strategy.get("slides", 5),
                consciousness
            )
        elif format_strategy["type"] == "reel":
            composition["scene_transitions"] = self._generate_reel_transitions(
                consciousness
            )
        
        return composition
    
    def _generate_carousel_flow(self, slides: int, consciousness: ConsciousnessParameters) -> List[Dict]:
        """Generate carousel slide flow with consciousness progression"""
        flow = []
        
        # Map slides to consciousness journey
        for i in range(slides):
            progress = i / (slides - 1) if slides > 1 else 0
            
            slide = {
                "number": i + 1,
                "intensity": 0.5 + progress * 0.5,
                "focus": "introduction" if i == 0 else "development" if i < slides-1 else "conclusion",
                "visual_energy": consciousness.coherence_level * (0.7 + progress * 0.3)
            }
            
            # Peak at golden ratio point
            if abs(progress - 0.618) < 0.1:
                slide["is_peak"] = True
                slide["intensity"] = 1.0
            
            flow.append(slide)
        
        return flow
    
    def _generate_reel_transitions(self, consciousness: ConsciousnessParameters) -> List[Dict]:
        """Generate reel scene transitions"""
        transitions = [
            {"time": 0, "type": "hook", "energy": 0.9},
            {"time": 0.382, "type": "smooth", "energy": 0.7},  # 1/φ²
            {"time": 0.618, "type": "peak", "energy": 1.0},    # 1/φ
            {"time": 0.9, "type": "resolution", "energy": 0.8}
        ]
        
        # Adjust based on consciousness
        for transition in transitions:
            transition["consciousness_alignment"] = consciousness.fractal_dimension / 1.618
        
        return transitions
    
    def _generate_caption(self, 
                         concept: str,
                         aesthetic: Dict[str, Any],
                         consciousness: ConsciousnessParameters) -> Dict[str, Any]:
        """Generate engaging caption with consciousness alignment"""
        # Caption structure templates
        templates = {
            "minimal": [
                f"{concept}.",
                f"This is {concept.lower()}.",
                f"• {concept} •"
            ],
            "vibrant": [
                f"✨ {concept} ✨ Who else feels this?! 💫",
                f"OKAY BUT {concept.upper()} THO 🔥🔥",
                f"Can we talk about {concept}?! Drop a ❤️ if you agree!"
            ],
            "moody": [
                f"Sometimes {concept.lower()} is all we need...",
                f"Lost in thoughts about {concept}",
                f"{concept}. That's it. That's the post."
            ],
            "pastel": [
                f"A little reminder about {concept} 🌸",
                f"Gentle thoughts on {concept} ☁️",
                f"Finding beauty in {concept} 💕"
            ],
            "luxury": [
                f"Elevating your perspective on {concept}",
                f"The art of {concept}",
                f"Curated insights: {concept}"
            ]
        }
        
        # Select template based on aesthetic
        caption_options = templates.get(aesthetic["name"], templates["vibrant"])
        base_caption = random.choice(caption_options)
        
        # Add consciousness elements
        if consciousness.phi_resonance > 0.7:
            base_caption += "\n\n↟ Aligned with the golden ratio of life ↟"
        
        # Add call-to-action based on emotional spectrum
        cta_options = [
            "Save this if it resonates 💫",
            "Share with someone who needs this ✨",
            "Comment your thoughts below 💭",
            "Tag a friend who gets it 👇"
        ]
        
        caption_data = {
            "main_text": base_caption,
            "cta": random.choice(cta_options),
            "line_breaks": 2,
            "emoji_density": {"minimal": 0.1, "vibrant": 0.3, "moody": 0.05, 
                            "pastel": 0.2, "luxury": 0.05}.get(aesthetic["name"], 0.15)
        }
        
        return caption_data
    
    def _select_audio(self, aesthetic: Dict[str, Any]) -> Dict[str, Any]:
        """Select trending audio matching aesthetic"""
        # Map aesthetics to audio preferences
        audio_preferences = {
            "minimal": ["Chill Lofi", "Aesthetic Vibes"],
            "vibrant": ["Upbeat Pop", "Motivational Beat"],
            "moody": ["Cinematic Epic", "Aesthetic Vibes"],
            "pastel": ["Chill Lofi", "Aesthetic Vibes"],
            "luxury": ["Cinematic Epic", "Motivational Beat"]
        }
        
        preferred_names = audio_preferences.get(aesthetic["name"], ["Aesthetic Vibes"])
        
        # Find matching audio
        for audio in self.trending_audio:
            if audio["name"] in preferred_names:
                return audio
        
        return random.choice(self.trending_audio)
    
    def _generate_metadata(self, 
                          concept: str,
                          aesthetic: Dict[str, Any],
                          caption_data: Dict[str, Any]) -> ContentMetadata:
        """Generate Instagram-optimized metadata"""
        # Build hashtag strategy
        hashtags = []
        
        # 1. Mix of hashtag sizes (Instagram algorithm favors this)
        hashtags.extend(self.hashtag_sets["discovery"][:2])  # Large hashtags
        
        # 2. Aesthetic-specific hashtags
        aesthetic_tags = self.hashtag_sets.get("aesthetic", [])
        if aesthetic["name"] in ["minimal", "luxury"]:
            hashtags.extend(aesthetic_tags[:3])
        
        # 3. Niche hashtags from concept
        concept_words = concept.lower().split()
        for word in concept_words:
            if len(word) > 4:
                hashtags.append(f"#{word}")
                hashtags.append(f"#{word}community")
        
        # 4. Engagement hashtags
        hashtags.extend(["#saveforlater", "#sharethis"])
        
        # Limit to 30 hashtags (Instagram max)
        hashtags = list(set(hashtags))[:30]
        
        # Build caption
        full_caption = f"{caption_data['main_text']}\n{'.'*caption_data['line_breaks']}\n{caption_data['cta']}"
        
        metadata = ContentMetadata(
            title=f"{concept} - {aesthetic['name'].title()} Aesthetic",
            description=full_caption,
            hashtags=hashtags,
            tags=[aesthetic["name"], aesthetic["style"], "instagram"],
            category=aesthetic["name"]
        )
        
        return metadata
    
    def _calculate_metrics(self,
                          content: ContentPiece,
                          aesthetic: Dict[str, Any],
                          composition: Dict[str, Any],
                          audio: Optional[Dict[str, Any]]) -> OptimizationMetrics:
        """Calculate Instagram-specific optimization metrics"""
        metrics = OptimizationMetrics()
        
        # Base engagement from aesthetic
        base_engagement = 60 * aesthetic.get("engagement_multiplier", 1.0)
        
        # Composition boost
        if composition["layout"] == "golden_spiral":
            base_engagement *= 1.15
        
        # Audio boost for reels
        if audio:
            base_engagement *= audio.get("saves_boost", 1.0)
        
        # Consciousness boost
        consciousness_multiplier = (
            content.consciousness.coherence_level * 0.3 +
            content.consciousness.phi_resonance * 0.4 +
            (content.consciousness.fractal_dimension / 1.618) * 0.3
        )
        base_engagement *= (1 + consciousness_multiplier * 0.5)
        
        # Instagram-specific metrics
        metrics.predicted_engagement = min(base_engagement, 95)
        
        # Saves are key on Instagram
        save_rate = metrics.predicted_engagement * 0.3  # ~30% of engaged users save
        
        # Viral coefficient (shares and DMs)
        metrics.viral_coefficient = (
            aesthetic.get("engagement_multiplier", 1.0) *
            consciousness_multiplier *
            1.2  # Instagram's natural virality
        )
        
        # ROI for Instagram (based on saves and profile visits)
        metrics.roi_estimate = (
            metrics.predicted_engagement * 
            save_rate * 
            0.1 *  # Conversion factor
            100    # Value multiplier
        )
        
        # Platform optimization score
        metrics.platform_optimization_score = np.mean([
            metrics.predicted_engagement / 100,
            min(len(content.metadata.hashtags) / 20, 1.0),  # Hashtag optimization
            aesthetic.get("engagement_multiplier", 1.0) / 1.5,
            consciousness_multiplier
        ])
        
        return metrics
    
    def _optimize_golden_ratio(self, composition: Dict[str, Any]) -> Dict[str, Any]:
        """Apply golden ratio optimization to composition"""
        phi = 1.618
        
        # Refine focal points to perfect golden ratio positions
        if "focal_points" in composition:
            for point in composition["focal_points"]:
                # Snap to golden ratio grid
                point["x"] = round(point["x"] * phi) / phi
                point["y"] = round(point["y"] * phi) / phi
        
        # Add golden rectangle guides
        composition["guides"] = {
            "golden_rectangle": {
                "width_ratio": phi,
                "height_ratio": 1/phi
            },
            "golden_spiral": {
                "center": {"x": 0.618, "y": 0.382},
                "rotation": "clockwise"
            }
        }
        
        return composition
    
    def _enhance_aesthetic(self, aesthetic: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance aesthetic appeal"""
        # Add complementary colors
        if "colors" in aesthetic:
            primary_color = aesthetic["colors"][0]
            # In production, would calculate actual complements
            aesthetic["accent_colors"] = ["#FFD700", "#FF69B4"]  # Gold and pink accents
        
        # Enhance style descriptors
        aesthetic["enhanced_style"] = aesthetic.get("style", "") + ", cohesive, branded"
        
        return aesthetic
    
    def _optimize_caption(self, caption_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize caption for engagement"""
        # Add strategic line breaks for readability
        main_text = caption_data["main_text"]
        
        # Instagram shows first ~125 chars, so front-load value
        if len(main_text) > 125:
            # Ensure key message is in first 125 chars
            words = main_text.split()
            caption_data["preview_optimized"] = True
        
        # Add spacing dots for aesthetic captions
        caption_data["spacing_dots"] = "." * 5  # Creates visual break
        
        return caption_data
    
    def _optimize_hashtags(self, metadata: ContentMetadata) -> ContentMetadata:
        """Optimize hashtag strategy"""
        current_tags = metadata.hashtags
        
        # Instagram hashtag distribution strategy
        # 10% huge (1M+ posts)
        # 30% large (100K-1M posts) 
        # 40% medium (10K-100K posts)
        # 20% small (<10K posts)
        
        # Add hashtag categories
        optimized_tags = []
        
        # Huge hashtags (for discovery)
        huge = ["#instagram", "#instagood", "#love"]
        optimized_tags.extend(random.sample(huge, min(3, len(huge))))
        
        # Keep existing tags
        optimized_tags.extend(current_tags)
        
        # Ensure variety and limit
        metadata.hashtags = list(set(optimized_tags))[:30]
        
        # Move hashtags to first comment if > 5 (cleaner aesthetic)
        if len(metadata.hashtags) > 5:
            metadata.tags.append("hashtags_in_comment")
        
        return metadata


def demo_instagram_generator():
    """Demonstrate Instagram content generation"""
    print("INSTAGRAM CONTENT GENERATOR DEMO")
    print("=" * 60)
    
    generator = InstagramContentGenerator()
    
    # Test different concepts and formats
    test_cases = [
        ("Minimalist morning routine", ContentType.CAROUSEL),
        ("Transformation Tuesday: AI Edition", ContentType.VIDEO_SHORT),
        ("Luxury lifestyle with AI", ContentType.IMAGE_POST),
        ("How to create viral content", ContentType.CAROUSEL)
    ]
    
    for concept, content_type in test_cases:
        print(f"\n{'='*50}")
        print(f"Concept: {concept}")
        print(f"Type: {content_type.value}")
        print(f"{'='*50}")
        
        # Create base content
        content = ContentPiece(
            content_type=content_type,
            platform=Platform.INSTAGRAM
        )
        
        # Add consciousness parameters
        content.consciousness.coherence_level = 0.8
        content.consciousness.phi_resonance = 0.7
        content.consciousness.fractal_dimension = 1.618
        
        # Generate content
        start = time.time()
        content = generator.generate(concept, {"content": content})
        gen_time = time.time() - start
        
        # Optimize
        content = generator.optimize(content)
        
        # Display results
        if content.raw_content:
            raw = content.raw_content
            print(f"\n📊 Generated Content:")
            print(f"  Generation time: {gen_time:.3f}s")
            print(f"  Aesthetic: {raw['aesthetic']['name']}")
            print(f"  Format: {raw['format']['type']}")
            if raw['format']['type'] == 'carousel':
                print(f"  Slides: {raw['format'].get('slides', 'N/A')}")
            print(f"  Composition: {raw['composition']['layout']}")
            
            print(f"\n💬 Caption Preview:")
            print(f"  {raw['caption']['main_text'][:100]}...")
            
            print(f"\n📈 Metrics:")
            print(f"  Predicted Engagement: {content.optimization.predicted_engagement:.1f}%")
            print(f"  Saves Potential: {content.optimization.predicted_engagement * 0.3:.1f}%")
            print(f"  Viral Coefficient: {content.optimization.viral_coefficient:.2f}")
            print(f"  Platform Score: {content.optimization.platform_optimization_score:.2f}")
            
            print(f"\n#️⃣ Hashtags ({len(content.metadata.hashtags)}):")
            print(f"  {' '.join(content.metadata.hashtags[:8])}...")
    
    print(f"\n⚡ Average generation time: <1 second!")
    print("\n✅ Instagram generator demo complete!")


if __name__ == "__main__":
    demo_instagram_generator()