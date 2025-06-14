#!/usr/bin/env python3
"""
Chakra Creativity Mapper
========================

Maps the 7-chakra consciousness system to creative content patterns,
enabling chakra-driven content generation and emotional journey design.
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class ChakraType(Enum):
    """Seven primary chakras"""
    ROOT = "root"           # Muladhara - Security, grounding
    SACRAL = "sacral"       # Svadhisthana - Creativity, emotion
    SOLAR = "solar"         # Manipura - Power, confidence
    HEART = "heart"         # Anahata - Love, connection
    THROAT = "throat"       # Vishuddha - Expression, truth
    THIRD_EYE = "third_eye" # Ajna - Intuition, wisdom
    CROWN = "crown"         # Sahasrara - Transcendence, unity


@dataclass
class ChakraProfile:
    """Profile for a single chakra"""
    chakra_type: ChakraType
    frequency: float  # Hz
    color: str
    element: str
    emotions: List[str]
    creative_themes: List[str]
    content_styles: List[str]
    engagement_triggers: List[str]


class ChakraCreativityMapper:
    """
    Maps chakra energies to creative content patterns
    """
    
    def __init__(self):
        self.chakra_profiles = self._initialize_chakra_profiles()
        self.creative_patterns = self._initialize_creative_patterns()
        
    def _initialize_chakra_profiles(self) -> Dict[ChakraType, ChakraProfile]:
        """Initialize detailed profiles for each chakra"""
        return {
            ChakraType.ROOT: ChakraProfile(
                chakra_type=ChakraType.ROOT,
                frequency=256.0,
                color="red",
                element="earth",
                emotions=["security", "stability", "trust", "grounding"],
                creative_themes=["foundation", "basics", "survival", "practical tips"],
                content_styles=["how-to", "tutorials", "life hacks", "safety tips"],
                engagement_triggers=["fear resolution", "practical value", "security needs"]
            ),
            
            ChakraType.SACRAL: ChakraProfile(
                chakra_type=ChakraType.SACRAL,
                frequency=288.0,
                color="orange",
                element="water",
                emotions=["creativity", "passion", "pleasure", "flow"],
                creative_themes=["creativity", "relationships", "emotions", "sensuality"],
                content_styles=["artistic", "emotional stories", "creative process", "behind-scenes"],
                engagement_triggers=["emotional connection", "creative inspiration", "pleasure"]
            ),
            
            ChakraType.SOLAR: ChakraProfile(
                chakra_type=ChakraType.SOLAR,
                frequency=320.0,
                color="yellow",
                element="fire",
                emotions=["confidence", "power", "will", "determination"],
                creative_themes=["empowerment", "achievement", "transformation", "leadership"],
                content_styles=["motivational", "success stories", "challenges", "transformation"],
                engagement_triggers=["personal power", "achievement desire", "confidence boost"]
            ),
            
            ChakraType.HEART: ChakraProfile(
                chakra_type=ChakraType.HEART,
                frequency=341.3,
                color="green",
                element="air",
                emotions=["love", "compassion", "joy", "connection"],
                creative_themes=["love", "kindness", "community", "healing"],
                content_styles=["heartwarming", "inspirational", "community stories", "acts of kindness"],
                engagement_triggers=["emotional resonance", "compassion", "shared humanity"]
            ),
            
            ChakraType.THROAT: ChakraProfile(
                chakra_type=ChakraType.THROAT,
                frequency=384.0,
                color="blue",
                element="ether",
                emotions=["expression", "truth", "communication", "authenticity"],
                creative_themes=["self-expression", "truth-telling", "communication", "authenticity"],
                content_styles=["personal stories", "truth bombs", "communication tips", "authentic sharing"],
                engagement_triggers=["truth recognition", "authentic expression", "communication needs"]
            ),
            
            ChakraType.THIRD_EYE: ChakraProfile(
                chakra_type=ChakraType.THIRD_EYE,
                frequency=426.7,
                color="indigo",
                element="light",
                emotions=["intuition", "insight", "wisdom", "clarity"],
                creative_themes=["wisdom", "intuition", "mysteries", "consciousness"],
                content_styles=["mind-blowing facts", "deep insights", "consciousness exploration", "mysteries"],
                engagement_triggers=["curiosity", "aha moments", "deep understanding"]
            ),
            
            ChakraType.CROWN: ChakraProfile(
                chakra_type=ChakraType.CROWN,
                frequency=512.0,
                color="violet",
                element="thought",
                emotions=["transcendence", "unity", "bliss", "enlightenment"],
                creative_themes=["spirituality", "unity", "purpose", "transcendence"],
                content_styles=["philosophical", "spiritual insights", "unity messages", "purpose-driven"],
                engagement_triggers=["spiritual connection", "unity consciousness", "higher purpose"]
            )
        }
    
    def _initialize_creative_patterns(self) -> Dict[str, Any]:
        """Initialize creative patterns for chakra combinations"""
        return {
            # Single chakra focus patterns
            "grounding": [ChakraType.ROOT],
            "creative_flow": [ChakraType.SACRAL],
            "empowerment": [ChakraType.SOLAR],
            "heart_opening": [ChakraType.HEART],
            "authentic_voice": [ChakraType.THROAT],
            "intuitive_wisdom": [ChakraType.THIRD_EYE],
            "spiritual_connection": [ChakraType.CROWN],
            
            # Multi-chakra journeys
            "hero_journey": [ChakraType.ROOT, ChakraType.SOLAR, ChakraType.HEART, ChakraType.CROWN],
            "creative_expression": [ChakraType.SACRAL, ChakraType.THROAT, ChakraType.THIRD_EYE],
            "love_story": [ChakraType.ROOT, ChakraType.SACRAL, ChakraType.HEART],
            "transformation": [ChakraType.SOLAR, ChakraType.HEART, ChakraType.THROAT, ChakraType.CROWN],
            "viral_ascension": [ChakraType.ROOT, ChakraType.SACRAL, ChakraType.SOLAR, 
                               ChakraType.HEART, ChakraType.THROAT]
        }
    
    def map_content_to_chakras(self, 
                              content_type: str,
                              concept: str,
                              target_emotion: Optional[str] = None) -> List[ChakraType]:
        """
        Map content concept to optimal chakra sequence
        
        Args:
            content_type: Type of content (video, image, text)
            concept: Content concept/theme
            target_emotion: Desired emotional outcome
            
        Returns:
            List of chakras for content journey
        """
        # Analyze concept for chakra alignment
        concept_lower = concept.lower()
        selected_chakras = []
        
        # Check each chakra's themes
        for chakra_type, profile in self.chakra_profiles.items():
            theme_match = any(theme in concept_lower for theme in profile.creative_themes)
            emotion_match = target_emotion and target_emotion in profile.emotions
            
            if theme_match or emotion_match:
                selected_chakras.append(chakra_type)
        
        # If no specific match, use default journey
        if not selected_chakras:
            if content_type == "video_short":
                selected_chakras = self.creative_patterns["viral_ascension"]
            elif content_type == "image_post":
                selected_chakras = self.creative_patterns["heart_opening"]
            else:
                selected_chakras = self.creative_patterns["creative_expression"]
        
        return selected_chakras
    
    def generate_emotional_arc(self, 
                             chakras: List[ChakraType],
                             duration: float = 15.0) -> Dict[str, Any]:
        """
        Generate emotional arc based on chakra sequence
        
        Args:
            chakras: Sequence of chakras
            duration: Content duration in seconds
            
        Returns:
            Emotional arc with timing and intensities
        """
        if not chakras:
            return {}
        
        arc = {
            "total_duration": duration,
            "segments": [],
            "peak_emotion": None,
            "emotional_journey": []
        }
        
        # Distribute time across chakras with golden ratio emphasis
        phi = 1.618
        if len(chakras) == 1:
            time_weights = [1.0]
        else:
            # Use fibonacci-like progression
            time_weights = []
            for i in range(len(chakras)):
                if i == len(chakras) // 2:  # Peak moment
                    time_weights.append(phi)
                else:
                    time_weights.append(1.0)
        
        # Normalize weights
        total_weight = sum(time_weights)
        time_distribution = [w / total_weight * duration for w in time_weights]
        
        # Build segments
        current_time = 0
        peak_intensity = 0
        
        for i, (chakra, segment_duration) in enumerate(zip(chakras, time_distribution)):
            profile = self.chakra_profiles[chakra]
            
            # Calculate intensity curve
            if i == 0:  # Start
                intensity = 0.7
            elif i == len(chakras) - 1:  # End
                intensity = 0.8
            elif i == len(chakras) // 2:  # Peak
                intensity = 1.0
            else:
                intensity = 0.6 + (i / len(chakras)) * 0.3
            
            segment = {
                "chakra": chakra.value,
                "start_time": current_time,
                "duration": segment_duration,
                "intensity": intensity,
                "frequency": profile.frequency,
                "emotions": profile.emotions,
                "color": profile.color,
                "engagement_triggers": profile.engagement_triggers
            }
            
            arc["segments"].append(segment)
            arc["emotional_journey"].extend(profile.emotions)
            
            if intensity > peak_intensity:
                peak_intensity = intensity
                arc["peak_emotion"] = profile.emotions[0]
            
            current_time += segment_duration
        
        return arc
    
    def optimize_for_platform(self, 
                            chakras: List[ChakraType],
                            platform: str) -> List[ChakraType]:
        """
        Optimize chakra sequence for specific platform
        
        Args:
            chakras: Initial chakra sequence
            platform: Target platform
            
        Returns:
            Optimized chakra sequence
        """
        platform_preferences = {
            "tiktok": {
                "max_chakras": 3,
                "preferred": [ChakraType.SACRAL, ChakraType.HEART, ChakraType.THROAT],
                "boost_energy": True
            },
            "instagram": {
                "max_chakras": 4,
                "preferred": [ChakraType.HEART, ChakraType.THIRD_EYE, ChakraType.SACRAL],
                "boost_energy": False
            },
            "youtube": {
                "max_chakras": 7,
                "preferred": [ChakraType.ROOT, ChakraType.SOLAR, ChakraType.CROWN],
                "boost_energy": False
            }
        }
        
        prefs = platform_preferences.get(platform, {"max_chakras": 5, "preferred": [], "boost_energy": False})
        
        # Limit chakras to platform maximum
        if len(chakras) > prefs["max_chakras"]:
            # Prioritize platform-preferred chakras
            optimized = []
            for chakra in prefs["preferred"]:
                if chakra in chakras and len(optimized) < prefs["max_chakras"]:
                    optimized.append(chakra)
            
            # Fill remaining slots
            for chakra in chakras:
                if chakra not in optimized and len(optimized) < prefs["max_chakras"]:
                    optimized.append(chakra)
            
            chakras = optimized
        
        # Boost energy for high-energy platforms
        if prefs["boost_energy"] and ChakraType.SACRAL not in chakras:
            chakras.insert(0, ChakraType.SACRAL)
            if len(chakras) > prefs["max_chakras"]:
                chakras = chakras[:prefs["max_chakras"]]
        
        return chakras
    
    def calculate_resonance_score(self, chakras: List[ChakraType]) -> float:
        """
        Calculate resonance score for chakra combination
        
        Args:
            chakras: List of chakras
            
        Returns:
            Resonance score (0-1)
        """
        if not chakras:
            return 0.0
        
        # Factors for high resonance
        factors = []
        
        # 1. Harmonic frequency relationships
        frequencies = [self.chakra_profiles[c].frequency for c in chakras]
        if len(frequencies) > 1:
            # Check for harmonic ratios
            ratios = []
            for i in range(len(frequencies) - 1):
                ratio = frequencies[i+1] / frequencies[i]
                # Check if close to musical intervals
                harmonic_score = max(
                    1 - abs(ratio - 1.5),      # Perfect fifth
                    1 - abs(ratio - 1.333),    # Perfect fourth
                    1 - abs(ratio - 1.25),     # Major third
                    1 - abs(ratio - 2.0)       # Octave
                ) * 2  # Scale to 0-1
                ratios.append(max(0, harmonic_score))
            factors.append(np.mean(ratios))
        
        # 2. Emotional coherence
        all_emotions = []
        for chakra in chakras:
            all_emotions.extend(self.chakra_profiles[chakra].emotions)
        
        # Unique emotions vs total (diversity is good)
        emotion_diversity = len(set(all_emotions)) / len(all_emotions) if all_emotions else 0
        factors.append(emotion_diversity)
        
        # 3. Journey completeness
        # Check if journey covers multiple levels
        chakra_levels = [c.value for c in chakras]
        has_grounding = any(c in [ChakraType.ROOT, ChakraType.SACRAL] for c in chakras)
        has_heart = ChakraType.HEART in chakras
        has_expression = any(c in [ChakraType.THROAT, ChakraType.THIRD_EYE] for c in chakras)
        
        completeness = sum([has_grounding, has_heart, has_expression]) / 3
        factors.append(completeness)
        
        # 4. Golden ratio alignment
        if len(chakras) in [3, 5, 8]:  # Fibonacci numbers
            factors.append(1.0)
        else:
            factors.append(0.7)
        
        return np.mean(factors) if factors else 0.5
    
    def generate_content_formula(self, chakras: List[ChakraType]) -> Dict[str, Any]:
        """
        Generate content creation formula based on chakras
        
        Args:
            chakras: Chakra sequence
            
        Returns:
            Content formula with specific guidance
        """
        formula = {
            "opening": [],
            "development": [],
            "climax": [],
            "resolution": [],
            "style_elements": set(),
            "emotional_hooks": set(),
            "visual_elements": set()
        }
        
        for i, chakra in enumerate(chakras):
            profile = self.chakra_profiles[chakra]
            
            # Map to content structure
            if i == 0:  # Opening
                formula["opening"].extend(profile.engagement_triggers)
                formula["emotional_hooks"].update(profile.emotions[:2])
            elif i == len(chakras) - 1:  # Resolution
                formula["resolution"].extend(profile.content_styles)
            elif i == len(chakras) // 2:  # Climax
                formula["climax"].extend(profile.creative_themes)
                formula["emotional_hooks"].update(profile.emotions)
            else:  # Development
                formula["development"].extend(profile.content_styles)
            
            # Collect style elements
            formula["style_elements"].update(profile.content_styles)
            formula["visual_elements"].add(profile.color)
            formula["visual_elements"].add(profile.element)
        
        # Convert sets to lists for JSON serialization
        formula["style_elements"] = list(formula["style_elements"])
        formula["emotional_hooks"] = list(formula["emotional_hooks"])
        formula["visual_elements"] = list(formula["visual_elements"])
        
        return formula


def demo_chakra_mapper():
    """Demonstrate chakra creativity mapping"""
    print("CHAKRA CREATIVITY MAPPER DEMO")
    print("=" * 60)
    
    mapper = ChakraCreativityMapper()
    
    # Test different content concepts
    test_cases = [
        ("How to build confidence", "video_short", "empowerment"),
        ("Love story that went viral", "video_short", "love"),
        ("Creative process behind my art", "image_post", "inspiration"),
        ("Meditation for beginners", "video_long", "peace")
    ]
    
    for concept, content_type, emotion in test_cases:
        print(f"\n{'='*50}")
        print(f"Concept: {concept}")
        print(f"Type: {content_type}")
        print(f"Target emotion: {emotion}")
        print(f"{'='*50}")
        
        # Map to chakras
        chakras = mapper.map_content_to_chakras(content_type, concept, emotion)
        print(f"\nChakra sequence: {[c.value for c in chakras]}")
        
        # Optimize for platform
        optimized = mapper.optimize_for_platform(chakras, "tiktok")
        print(f"Optimized for TikTok: {[c.value for c in optimized]}")
        
        # Generate emotional arc
        arc = mapper.generate_emotional_arc(optimized, duration=15.0)
        print(f"\nEmotional arc:")
        for segment in arc["segments"]:
            print(f"  {segment['chakra']}: {segment['duration']:.1f}s @ {segment['intensity']:.1f} intensity")
        print(f"Peak emotion: {arc['peak_emotion']}")
        
        # Calculate resonance
        resonance = mapper.calculate_resonance_score(optimized)
        print(f"\nResonance score: {resonance:.2f}")
        
        # Generate content formula
        formula = mapper.generate_content_formula(optimized)
        print(f"\nContent formula:")
        print(f"  Opening hooks: {formula['opening'][:2]}")
        print(f"  Style elements: {formula['style_elements'][:3]}")
        print(f"  Emotional hooks: {formula['emotional_hooks']}")
    
    print("\n✅ Chakra mapper demo complete!")


if __name__ == "__main__":
    demo_chakra_mapper()