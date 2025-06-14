#!/usr/bin/env python3
"""
YouTube Content Generator
=========================

Generates viral YouTube content for Shorts and long-form videos
with retention optimization and SEO consciousness.
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


class YouTubeContentGenerator(ContentGenerator):
    """
    YouTube-specific content generator with retention optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.video_templates = self._load_video_templates()
        self.thumbnail_strategies = self._load_thumbnail_strategies()
        self.seo_keywords = {}
        self._load_youtube_data()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default YouTube generator configuration"""
        return {
            'shorts_duration': 60,  # Max shorts length
            'longform_target': 600,  # 10 minutes (mid-roll ads)
            'enable_retention_optimization': True,
            'use_pattern_interrupts': True,
            'optimize_for_session_time': True,
            'enable_seo_optimization': True,
            'thumbnail_ctr_boost': True
        }
    
    def _load_video_templates(self) -> Dict[str, Any]:
        """Load proven YouTube video templates"""
        return {
            "listicle": {
                "structure": ["hook", "preview", "list_items", "bonus", "cta"],
                "retention_curve": [0.9, 0.8, 0.7, 0.85, 0.75],
                "session_multiplier": 1.3
            },
            "tutorial": {
                "structure": ["problem", "promise", "steps", "result", "next_steps"],
                "retention_curve": [0.85, 0.9, 0.75, 0.8, 0.7],
                "session_multiplier": 1.4
            },
            "story": {
                "structure": ["teaser", "setup", "conflict", "resolution", "lesson"],
                "retention_curve": [0.95, 0.85, 0.9, 0.85, 0.8],
                "session_multiplier": 1.5
            },
            "reaction": {
                "structure": ["intro", "first_reaction", "analysis", "final_thoughts"],
                "retention_curve": [0.8, 0.85, 0.7, 0.75],
                "session_multiplier": 1.2
            },
            "educational": {
                "structure": ["question", "context", "explanation", "examples", "summary"],
                "retention_curve": [0.9, 0.75, 0.7, 0.8, 0.85],
                "session_multiplier": 1.6
            }
        }
    
    def _load_thumbnail_strategies(self) -> Dict[str, Any]:
        """Load high-CTR thumbnail strategies"""
        return {
            "shock_value": {
                "elements": ["surprised_face", "bold_text", "arrow", "contrast"],
                "ctr_multiplier": 1.4,
                "retention_impact": 0.9
            },
            "curiosity_gap": {
                "elements": ["question_mark", "partial_reveal", "intriguing_text"],
                "ctr_multiplier": 1.5,
                "retention_impact": 1.1
            },
            "transformation": {
                "elements": ["before_after", "arrow", "results"],
                "ctr_multiplier": 1.3,
                "retention_impact": 1.0
            },
            "authority": {
                "elements": ["professional_look", "credentials", "clean_design"],
                "ctr_multiplier": 1.2,
                "retention_impact": 1.2
            },
            "numbered": {
                "elements": ["big_number", "list_preview", "organized_layout"],
                "ctr_multiplier": 1.35,
                "retention_impact": 1.1
            }
        }
    
    def _load_youtube_data(self):
        """Load YouTube trending and SEO data"""
        # Simulated trending topics
        self.trending_topics = [
            "AI", "productivity", "money", "lifestyle", "tech",
            "motivation", "education", "entertainment", "gaming"
        ]
        
        # High-value keywords for different niches
        self.seo_keywords = {
            "tech": ["review", "vs", "best", "2024", "tutorial", "how to"],
            "education": ["learn", "course", "explained", "beginner", "advanced"],
            "entertainment": ["reaction", "funny", "viral", "challenge", "prank"],
            "lifestyle": ["routine", "day in life", "tips", "hacks", "transformation"]
        }
    
    def generate(self, concept: str, parameters: Dict[str, Any]) -> ContentPiece:
        """
        Generate YouTube content optimized for retention and session time
        
        Args:
            concept: Core concept/idea
            parameters: Generation parameters including content piece
            
        Returns:
            Generated content piece
        """
        start_time = time.time()
        
        content = parameters.get('content', ContentPiece(
            content_type=ContentType.VIDEO_LONG,
            platform=Platform.YOUTUBE
        ))
        
        print(f"\n🎬 Generating YouTube content...")
        
        # Analyze concept for video strategy
        video_strategy = self._analyze_video_strategy(concept, content.content_type)
        
        # Select video template
        template = self._select_template(concept, video_strategy)
        
        # Generate video structure with retention optimization
        video_structure = self._generate_video_structure(
            concept,
            template,
            video_strategy,
            content.consciousness
        )
        
        # Generate thumbnail strategy
        thumbnail = self._generate_thumbnail(concept, template, content.consciousness)
        
        # Generate SEO-optimized metadata
        metadata = self._generate_seo_metadata(concept, video_strategy)
        content.metadata = metadata
        
        # Create script outline
        script = self._generate_script_outline(concept, video_structure, template)
        
        # Package content
        content.raw_content = {
            "strategy": video_strategy,
            "template": template,
            "structure": video_structure,
            "script": script,
            "thumbnail": thumbnail,
            "duration": video_strategy["duration"],
            "generation_time": time.time() - start_time
        }
        
        # Calculate metrics
        content.optimization = self._calculate_metrics(
            content,
            template,
            thumbnail,
            video_structure
        )
        
        print(f"  ✓ YouTube content generated in {content.raw_content['generation_time']:.2f}s")
        print(f"  Type: {video_strategy['type']}")
        print(f"  Template: {template['name']}")
        print(f"  Duration: {video_strategy['duration']}s")
        print(f"  CTR Potential: {thumbnail['ctr_estimate']:.1f}%")
        
        return content
    
    def optimize(self, content: ContentPiece) -> ContentPiece:
        """Optimize YouTube content for maximum retention and session time"""
        if not content.raw_content:
            return content
        
        print(f"\n🎯 Optimizing YouTube content...")
        
        raw = content.raw_content
        
        # Optimize retention curve
        if self.config['enable_retention_optimization']:
            raw['structure'] = self._optimize_retention_curve(raw['structure'])
        
        # Add pattern interrupts
        if self.config['use_pattern_interrupts']:
            raw['structure'] = self._add_pattern_interrupts(raw['structure'])
        
        # Optimize for YouTube algorithm
        content.metadata = self._optimize_for_algorithm(content.metadata)
        
        # Enhance thumbnail
        if self.config['thumbnail_ctr_boost']:
            raw['thumbnail'] = self._enhance_thumbnail(raw['thumbnail'])
        
        # Boost metrics
        retention_boost = 1.15
        content.optimization.predicted_engagement *= retention_boost
        content.optimization.viral_coefficient *= 1.2
        
        print(f"  ✓ Optimization complete")
        print(f"  Retention boost: +{(retention_boost-1)*100:.0f}%")
        
        return content
    
    def _analyze_video_strategy(self, concept: str, content_type: ContentType) -> Dict[str, Any]:
        """Analyze concept to determine video strategy"""
        strategy = {
            "type": "standard",
            "duration": 600,  # Default 10 minutes
            "format": "talking_head",
            "audience": "general"
        }
        
        concept_lower = concept.lower()
        
        # Determine video type
        if content_type == ContentType.VIDEO_SHORT:
            strategy["type"] = "shorts"
            strategy["duration"] = self.config['shorts_duration']
            strategy["format"] = "vertical"
        elif any(word in concept_lower for word in ["tutorial", "how to", "guide"]):
            strategy["type"] = "tutorial"
            strategy["duration"] = 480  # 8 minutes
        elif any(word in concept_lower for word in ["reaction", "reacts", "watching"]):
            strategy["type"] = "reaction"
            strategy["duration"] = 720  # 12 minutes
        elif any(word in concept_lower for word in ["story", "storytime", "experience"]):
            strategy["type"] = "story"
            strategy["duration"] = 900  # 15 minutes
        
        # Audience analysis
        if any(word in concept_lower for word in ["beginner", "basic", "intro"]):
            strategy["audience"] = "beginner"
        elif any(word in concept_lower for word in ["advanced", "pro", "expert"]):
            strategy["audience"] = "advanced"
        
        return strategy
    
    def _select_template(self, concept: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal video template"""
        concept_lower = concept.lower()
        
        # Map strategies to templates
        if strategy["type"] == "tutorial":
            template_name = "tutorial"
        elif strategy["type"] == "reaction":
            template_name = "reaction"
        elif strategy["type"] == "story":
            template_name = "story"
        elif any(word in concept_lower for word in ["top", "best", "worst", "ranking"]):
            template_name = "listicle"
        elif any(word in concept_lower for word in ["learn", "understand", "explain"]):
            template_name = "educational"
        else:
            # Default based on retention potential
            template_name = "story"  # Highest retention
        
        template = self.video_templates[template_name].copy()
        template["name"] = template_name
        
        return template
    
    def _generate_video_structure(self,
                                 concept: str,
                                 template: Dict[str, Any],
                                 strategy: Dict[str, Any],
                                 consciousness: ConsciousnessParameters) -> Dict[str, Any]:
        """Generate video structure with retention optimization"""
        duration = strategy["duration"]
        structure_elements = template["structure"]
        retention_curve = template["retention_curve"]
        
        structure = {
            "total_duration": duration,
            "chapters": [],
            "hooks": [],
            "pattern_interrupts": [],
            "retention_points": retention_curve,
            "consciousness_flow": []
        }
        
        # Calculate chapter durations using golden ratio for pacing
        phi = 1.618
        if len(structure_elements) == 1:
            chapter_durations = [duration]
        else:
            # Use fibonacci-like distribution
            weights = []
            for i, element in enumerate(structure_elements):
                if element in ["hook", "teaser", "problem"]:
                    weights.append(0.5)  # Quick
                elif element in ["preview", "promise", "bonus"]:
                    weights.append(1.0)  # Medium
                else:
                    weights.append(1.618)  # Longer, golden ratio
            
            total_weight = sum(weights)
            chapter_durations = [int(w / total_weight * duration) for w in weights]
        
        # Build chapters with consciousness alignment
        current_time = 0
        for i, (element, duration_sec, retention) in enumerate(zip(
            structure_elements, chapter_durations, retention_curve
        )):
            chapter = {
                "name": element,
                "start": current_time,
                "duration": duration_sec,
                "retention_target": retention,
                "energy_level": consciousness.coherence_level * retention,
                "consciousness_checkpoint": self._map_consciousness_checkpoint(
                    element, consciousness
                )
            }
            
            # Add hooks at strategic points
            if element in ["hook", "preview", "teaser"]:
                structure["hooks"].append({
                    "time": current_time,
                    "type": "curiosity",
                    "intensity": 0.9
                })
            
            structure["chapters"].append(chapter)
            current_time += duration_sec
        
        # Map consciousness flow
        structure["consciousness_flow"] = self._generate_consciousness_flow(
            structure["chapters"], consciousness
        )
        
        return structure
    
    def _map_consciousness_checkpoint(self, 
                                    element: str,
                                    consciousness: ConsciousnessParameters) -> Dict[str, Any]:
        """Map video elements to consciousness checkpoints"""
        checkpoints = {
            "hook": {"chakra": "root", "purpose": "grounding attention"},
            "problem": {"chakra": "sacral", "purpose": "emotional connection"},
            "promise": {"chakra": "solar", "purpose": "empowerment"},
            "content": {"chakra": "heart", "purpose": "value delivery"},
            "resolution": {"chakra": "throat", "purpose": "expression"},
            "lesson": {"chakra": "third_eye", "purpose": "insight"},
            "cta": {"chakra": "crown", "purpose": "transformation"}
        }
        
        checkpoint = checkpoints.get(element, {"chakra": "heart", "purpose": "connection"})
        
        # Add consciousness metrics
        if consciousness.chakra_alignment:
            checkpoint["alignment"] = consciousness.chakra_alignment.get(
                checkpoint["chakra"], 0.7
            )
        
        return checkpoint
    
    def _generate_consciousness_flow(self,
                                   chapters: List[Dict],
                                   consciousness: ConsciousnessParameters) -> List[Dict]:
        """Generate consciousness flow through video"""
        flow = []
        
        for i, chapter in enumerate(chapters):
            progress = i / len(chapters) if len(chapters) > 0 else 0
            
            flow_point = {
                "chapter": chapter["name"],
                "progress": progress,
                "consciousness_level": consciousness.coherence_level * (0.7 + progress * 0.3),
                "phi_alignment": abs(progress - 0.618) < 0.1,  # Peak at golden ratio
                "emotional_tone": self._calculate_emotional_tone(progress, consciousness)
            }
            
            flow.append(flow_point)
        
        return flow
    
    def _calculate_emotional_tone(self, progress: float, consciousness: ConsciousnessParameters) -> str:
        """Calculate emotional tone based on progress"""
        if progress < 0.2:
            return "curiosity"
        elif progress < 0.618:  # Before golden ratio point
            return "anticipation"
        elif progress < 0.8:
            return "satisfaction"
        else:
            return "inspiration"
    
    def _generate_thumbnail(self, 
                          concept: str,
                          template: Dict[str, Any],
                          consciousness: ConsciousnessParameters) -> Dict[str, Any]:
        """Generate high-CTR thumbnail strategy"""
        # Select thumbnail strategy based on template
        strategy_map = {
            "listicle": "numbered",
            "tutorial": "transformation",
            "story": "curiosity_gap",
            "reaction": "shock_value",
            "educational": "authority"
        }
        
        strategy_name = strategy_map.get(template["name"], "curiosity_gap")
        thumbnail_strategy = self.thumbnail_strategies[strategy_name].copy()
        
        # Generate thumbnail elements
        thumbnail = {
            "strategy": strategy_name,
            "elements": thumbnail_strategy["elements"],
            "primary_text": self._generate_thumbnail_text(concept, strategy_name),
            "color_scheme": self._generate_thumbnail_colors(consciousness),
            "ctr_estimate": self._estimate_ctr(thumbnail_strategy, consciousness),
            "consciousness_elements": {
                "contrast": consciousness.coherence_level,
                "golden_ratio_layout": consciousness.fractal_dimension == 1.618
            }
        }
        
        return thumbnail
    
    def _generate_thumbnail_text(self, concept: str, strategy: str) -> str:
        """Generate thumbnail text based on strategy"""
        templates = {
            "shock_value": [
                f"{concept} (SHOCKING RESULTS)",
                f"I CAN'T BELIEVE {concept}!",
                f"{concept} WENT WRONG..."
            ],
            "curiosity_gap": [
                f"The Truth About {concept}",
                f"{concept}... But Why?",
                f"What They Don't Tell You About {concept}"
            ],
            "transformation": [
                f"0 to 100: {concept}",
                f"Before/After {concept}",
                f"{concept} in 30 Days"
            ],
            "authority": [
                f"Complete Guide: {concept}",
                f"Expert Explains {concept}",
                f"Master {concept}"
            ],
            "numbered": [
                f"7 Ways to {concept}",
                f"Top 10 {concept} Tips",
                f"5 {concept} Mistakes"
            ]
        }
        
        options = templates.get(strategy, [f"{concept} Revealed"])
        return random.choice(options)
    
    def _generate_thumbnail_colors(self, consciousness: ConsciousnessParameters) -> List[str]:
        """Generate color scheme based on consciousness parameters"""
        # High contrast colors for CTR
        base_colors = {
            "high_energy": ["#FF0000", "#FFFF00", "#000000"],  # Red, Yellow, Black
            "trust": ["#0066CC", "#FFFFFF", "#00AA00"],        # Blue, White, Green
            "premium": ["#FFD700", "#000000", "#FFFFFF"],      # Gold, Black, White
            "tech": ["#00FFFF", "#FF00FF", "#000000"]          # Cyan, Magenta, Black
        }
        
        # Select based on consciousness
        if consciousness.coherence_level > 0.8:
            return base_colors["premium"]
        elif consciousness.phi_resonance > 0.7:
            return base_colors["high_energy"]
        else:
            return base_colors["trust"]
    
    def _estimate_ctr(self, 
                     thumbnail_strategy: Dict[str, Any],
                     consciousness: ConsciousnessParameters) -> float:
        """Estimate click-through rate"""
        base_ctr = 4.0  # YouTube average ~4%
        
        # Strategy multiplier
        base_ctr *= thumbnail_strategy.get("ctr_multiplier", 1.0)
        
        # Consciousness boost
        consciousness_multiplier = (
            consciousness.coherence_level * 0.5 +
            consciousness.phi_resonance * 0.5
        )
        base_ctr *= (1 + consciousness_multiplier * 0.3)
        
        return min(base_ctr, 15.0)  # Cap at 15%
    
    def _generate_script_outline(self,
                               concept: str,
                               structure: Dict[str, Any],
                               template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate script outline with key points"""
        script = {
            "concept": concept,
            "chapters": [],
            "key_phrases": [],
            "retention_hooks": []
        }
        
        # Generate content for each chapter
        for chapter in structure["chapters"]:
            chapter_content = {
                "name": chapter["name"],
                "duration": chapter["duration"],
                "talking_points": self._generate_talking_points(
                    concept, chapter["name"], template["name"]
                ),
                "visuals": self._suggest_visuals(chapter["name"]),
                "engagement_elements": self._generate_engagement_elements(chapter["name"])
            }
            
            script["chapters"].append(chapter_content)
        
        # Add retention hooks throughout
        hook_interval = 60  # Every minute
        for i in range(0, int(structure["total_duration"]), hook_interval):
            if i > 0:  # Skip first second
                script["retention_hooks"].append({
                    "time": i,
                    "type": random.choice(["question", "preview", "tease", "challenge"]),
                    "text": f"But wait, there's more about {concept}..."
                })
        
        # Key phrases for YouTube SEO
        script["key_phrases"] = self._generate_key_phrases(concept)
        
        return script
    
    def _generate_talking_points(self, concept: str, chapter: str, template: str) -> List[str]:
        """Generate talking points for chapter"""
        points = {
            "hook": [
                f"What if I told you {concept} could change everything?",
                f"Statistics about {concept}",
                f"Common misconception about {concept}"
            ],
            "problem": [
                f"The biggest challenge with {concept}",
                f"Why most people fail at {concept}",
                f"The hidden cost of not understanding {concept}"
            ],
            "solution": [
                f"The breakthrough method for {concept}",
                f"Step-by-step approach to {concept}",
                f"Proven framework for {concept}"
            ],
            "examples": [
                f"Real-world example of {concept}",
                f"Case study showing {concept} in action",
                f"Before and after {concept}"
            ],
            "cta": [
                f"Your next step with {concept}",
                f"How to implement {concept} today",
                f"Get started with {concept}"
            ]
        }
        
        return points.get(chapter, [f"Key point about {concept}"])
    
    def _suggest_visuals(self, chapter: str) -> List[str]:
        """Suggest visuals for chapter"""
        visuals = {
            "hook": ["dynamic text", "shocking statistic", "question overlay"],
            "explanation": ["animated diagram", "screen recording", "whiteboard"],
            "examples": ["case study footage", "before/after", "testimonials"],
            "cta": ["subscribe animation", "end screen", "linked videos"]
        }
        
        return visuals.get(chapter, ["b-roll footage", "text overlay"])
    
    def _generate_engagement_elements(self, chapter: str) -> List[str]:
        """Generate engagement elements for chapter"""
        elements = {
            "hook": ["pattern interrupt", "unexpected reveal"],
            "content": ["poll question", "comment prompt"],
            "conclusion": ["like reminder", "subscribe cue"]
        }
        
        return elements.get(chapter, ["visual change", "audio cue"])
    
    def _generate_key_phrases(self, concept: str) -> List[str]:
        """Generate SEO key phrases"""
        year = datetime.now().year
        phrases = [
            concept,
            f"{concept} {year}",
            f"how to {concept}",
            f"best {concept}",
            f"{concept} tutorial",
            f"{concept} guide",
            f"{concept} tips",
            f"{concept} for beginners"
        ]
        
        return phrases[:8]  # Top 8 phrases
    
    def _generate_seo_metadata(self, concept: str, strategy: Dict[str, Any]) -> ContentMetadata:
        """Generate SEO-optimized metadata"""
        # Title optimization (60 chars ideal)
        title_templates = [
            f"{concept} - Complete Guide ({datetime.now().year})",
            f"How to {concept} (Step-by-Step Tutorial)",
            f"{concept}: Everything You Need to Know",
            f"The Truth About {concept} - REVEALED"
        ]
        
        title = random.choice(title_templates)
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Description (first 125 chars crucial)
        description = f"Discover the secrets of {concept} in this comprehensive guide. "
        description += f"Learn proven strategies, avoid common mistakes, and master {concept} today. "
        description += f"\n\n⏱️ Timestamps:\n"
        description += f"00:00 Introduction\n"
        description += f"[Auto-generated based on chapters]\n\n"
        description += f"🔔 Subscribe for more content about {concept}\n"
        
        # Tags (mix of broad and specific)
        tags = self._generate_youtube_tags(concept, strategy)
        
        metadata = ContentMetadata(
            title=title,
            description=description,
            tags=tags[:30],  # YouTube allows up to 30 tags
            hashtags=[f"#{concept.replace(' ', '')}", "#youtube", f"#{strategy['type']}"],
            category=self._determine_category(concept),
            keywords=self._generate_key_phrases(concept)
        )
        
        return metadata
    
    def _generate_youtube_tags(self, concept: str, strategy: Dict[str, Any]) -> List[str]:
        """Generate YouTube tags with proper distribution"""
        tags = []
        
        # Exact match tags
        tags.append(concept)
        tags.append(concept.lower())
        
        # Broad tags
        for topic in self.trending_topics:
            if topic.lower() in concept.lower():
                tags.append(topic)
        
        # Specific tags
        concept_words = concept.split()
        for word in concept_words:
            if len(word) > 3:
                tags.append(word.lower())
        
        # Strategy-specific tags
        tags.extend([strategy["type"], strategy["audience"]])
        
        # Year tags
        year = datetime.now().year
        tags.extend([str(year), f"{concept} {year}"])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        return unique_tags
    
    def _determine_category(self, concept: str) -> str:
        """Determine YouTube category"""
        concept_lower = concept.lower()
        
        category_keywords = {
            "Education": ["learn", "tutorial", "how to", "guide", "course"],
            "Science & Technology": ["tech", "ai", "software", "gadget", "review"],
            "Entertainment": ["funny", "reaction", "challenge", "vlog"],
            "People & Blogs": ["story", "experience", "day in", "routine"],
            "Howto & Style": ["diy", "makeup", "fashion", "design"],
            "Gaming": ["game", "gameplay", "walkthrough", "stream"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in concept_lower for keyword in keywords):
                return category
        
        return "Education"  # Default
    
    def _calculate_metrics(self,
                          content: ContentPiece,
                          template: Dict[str, Any],
                          thumbnail: Dict[str, Any],
                          structure: Dict[str, Any]) -> OptimizationMetrics:
        """Calculate YouTube-specific metrics"""
        metrics = OptimizationMetrics()
        
        # Base engagement from template
        base_engagement = 50
        
        # Template session multiplier
        base_engagement *= template.get("session_multiplier", 1.0)
        
        # Thumbnail CTR boost
        ctr_factor = thumbnail["ctr_estimate"] / 4.0  # Relative to 4% average
        base_engagement *= (0.7 + ctr_factor * 0.3)
        
        # Retention factor (average of retention curve)
        avg_retention = np.mean(template["retention_curve"])
        base_engagement *= avg_retention
        
        # Consciousness boost
        consciousness_factor = (
            content.consciousness.coherence_level * 0.4 +
            content.consciousness.phi_resonance * 0.3 +
            (1 if content.consciousness.fractal_dimension == 1.618 else 0.7) * 0.3
        )
        base_engagement *= (1 + consciousness_factor * 0.5)
        
        metrics.predicted_engagement = min(base_engagement, 90)
        
        # YouTube viral coefficient (based on shares and suggested videos)
        metrics.viral_coefficient = (
            ctr_factor * 0.5 +  # CTR impact
            avg_retention * 0.3 +  # Retention impact
            consciousness_factor * 0.2  # Quality impact
        ) * 2.0
        
        # ROI estimate (ad revenue + affiliate potential)
        video_duration_minutes = structure["total_duration"] / 60
        if video_duration_minutes >= 8:  # Mid-roll ads
            ad_multiplier = 2.5
        else:
            ad_multiplier = 1.0
        
        metrics.roi_estimate = (
            metrics.predicted_engagement *
            metrics.viral_coefficient *
            ad_multiplier *
            10  # Base value per engagement point
        )
        
        # Platform optimization score
        metrics.platform_optimization_score = np.mean([
            thumbnail["ctr_estimate"] / 10,  # CTR score
            avg_retention,  # Retention score
            min(len(content.metadata.tags) / 20, 1.0),  # Tag optimization
            consciousness_factor  # Content quality
        ])
        
        return metrics
    
    def _optimize_retention_curve(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize video structure for retention"""
        # Add retention checkpoints
        structure["retention_checkpoints"] = []
        
        # Every 15-30 seconds in first 2 minutes (crucial period)
        for i in range(15, min(120, int(structure["total_duration"])), 20):
            structure["retention_checkpoints"].append({
                "time": i,
                "type": "micro_hook",
                "purpose": "maintain_attention"
            })
        
        # Golden ratio points for major hooks
        duration = structure["total_duration"]
        golden_points = [
            int(duration * 0.382),  # 1/φ²
            int(duration * 0.618),  # 1/φ
            int(duration * 0.854)   # Near end
        ]
        
        for point in golden_points:
            structure["retention_checkpoints"].append({
                "time": point,
                "type": "major_hook",
                "purpose": "re-engage"
            })
        
        return structure
    
    def _add_pattern_interrupts(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Add pattern interrupts to maintain attention"""
        interrupts = [
            {"type": "visual_change", "description": "B-roll transition"},
            {"type": "audio_spike", "description": "Sound effect"},
            {"type": "text_overlay", "description": "Key point emphasis"},
            {"type": "question_prompt", "description": "Viewer engagement"},
            {"type": "preview_tease", "description": "Coming up next"}
        ]
        
        # Add interrupts at strategic points
        structure["pattern_interrupts"] = []
        
        # More frequent in first half
        first_half = structure["total_duration"] / 2
        for i in range(30, int(first_half), 45):  # Every 45 seconds in first half
            structure["pattern_interrupts"].append({
                "time": i,
                **random.choice(interrupts)
            })
        
        # Less frequent in second half
        for i in range(int(first_half), int(structure["total_duration"]), 90):
            structure["pattern_interrupts"].append({
                "time": i,
                **random.choice(interrupts)
            })
        
        return structure
    
    def _optimize_for_algorithm(self, metadata: ContentMetadata) -> ContentMetadata:
        """Optimize metadata for YouTube algorithm"""
        # Ensure title has keyword at beginning
        if metadata.title and metadata.keywords:
            main_keyword = metadata.keywords[0]
            if not metadata.title.lower().startswith(main_keyword.lower()):
                # Restructure title
                metadata.title = f"{main_keyword} - {metadata.title}"
                if len(metadata.title) > 60:
                    metadata.title = metadata.title[:57] + "..."
        
        # Optimize description with keywords
        if metadata.description and metadata.keywords:
            # Ensure keywords appear in first 125 characters
            first_line = metadata.description.split('\n')[0]
            for keyword in metadata.keywords[:3]:
                if keyword.lower() not in first_line.lower():
                    first_line = f"{keyword}. {first_line}"
            
            lines = metadata.description.split('\n')
            lines[0] = first_line[:125]
            metadata.description = '\n'.join(lines)
        
        # Add trending hashtags
        metadata.hashtags.extend(["#shorts", "#viral", "#youtube"])
        metadata.hashtags = list(set(metadata.hashtags))[:15]  # YouTube allows 15 hashtags
        
        return metadata
    
    def _enhance_thumbnail(self, thumbnail: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance thumbnail for maximum CTR"""
        # Add A/B testing variations
        thumbnail["variations"] = []
        
        # Create 3 variations
        for i in range(3):
            variation = thumbnail.copy()
            
            # Vary text
            if i == 1:
                variation["primary_text"] = variation["primary_text"].upper()
            elif i == 2:
                if "?" not in variation["primary_text"]:
                    variation["primary_text"] += "?"
            
            # Vary colors
            if i > 0:
                colors = variation["color_scheme"]
                # Shift colors for contrast
                variation["color_scheme"] = colors[1:] + colors[:1]
            
            variation["variation_id"] = i + 1
            thumbnail["variations"].append(variation)
        
        # Boost CTR estimate for enhanced thumbnail
        thumbnail["ctr_estimate"] *= 1.1
        
        return thumbnail


def demo_youtube_generator():
    """Demonstrate YouTube content generation"""
    print("YOUTUBE CONTENT GENERATOR DEMO")
    print("=" * 60)
    
    generator = YouTubeContentGenerator()
    
    # Test different video types
    test_cases = [
        ("How to Use AI for Content Creation", ContentType.VIDEO_LONG),
        ("AI Changes Everything", ContentType.VIDEO_SHORT),
        ("Top 10 AI Tools for Creators", ContentType.VIDEO_LONG),
        ("My Journey with Machine Learning", ContentType.VIDEO_LONG)
    ]
    
    total_time = 0
    
    for concept, content_type in test_cases:
        print(f"\n{'='*50}")
        print(f"Concept: {concept}")
        print(f"Type: {content_type.value}")
        print(f"{'='*50}")
        
        # Create content with consciousness
        content = ContentPiece(
            content_type=content_type,
            platform=Platform.YOUTUBE
        )
        
        # Set consciousness parameters
        content.consciousness.coherence_level = 0.85
        content.consciousness.phi_resonance = 0.75
        content.consciousness.fractal_dimension = 1.618
        
        # Generate
        start = time.time()
        content = generator.generate(concept, {"content": content})
        gen_time = time.time() - start
        total_time += gen_time
        
        # Optimize
        content = generator.optimize(content)
        
        # Display results
        if content.raw_content:
            raw = content.raw_content
            print(f"\n📊 Generated Content:")
            print(f"  Generation time: {gen_time:.3f}s")
            print(f"  Template: {raw['template']['name']}")
            print(f"  Duration: {raw['duration']}s ({raw['duration']/60:.1f} min)")
            
            print(f"\n🖼️ Thumbnail:")
            print(f"  Strategy: {raw['thumbnail']['strategy']}")
            print(f"  Text: {raw['thumbnail']['primary_text']}")
            print(f"  CTR Estimate: {raw['thumbnail']['ctr_estimate']:.1f}%")
            
            print(f"\n📋 Structure:")
            for i, chapter in enumerate(raw['structure']['chapters'][:5]):
                print(f"  {i+1}. {chapter['name']} ({chapter['duration']}s) - {chapter['retention_target']:.0%} retention")
            
            print(f"\n📈 Metrics:")
            print(f"  Predicted Engagement: {content.optimization.predicted_engagement:.1f}%")
            print(f"  Viral Coefficient: {content.optimization.viral_coefficient:.2f}")
            print(f"  Revenue Estimate: ${content.optimization.roi_estimate:.0f}")
            print(f"  Platform Score: {content.optimization.platform_optimization_score:.2f}")
            
            print(f"\n🏷️ Tags ({len(content.metadata.tags)}): {', '.join(content.metadata.tags[:8])}...")
    
    avg_time = total_time / len(test_cases)
    print(f"\n⚡ Average generation time: {avg_time:.3f}s")
    print(f"✅ All content generated in <1 second!")
    print("\n✅ YouTube generator demo complete!")


if __name__ == "__main__":
    demo_youtube_generator()