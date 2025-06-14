#!/usr/bin/env python3
"""
Content Types and Data Structures
=================================

Defines the core content types and data structures used throughout
the ProStudio SDK for social media content generation.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class ContentType(Enum):
    """Supported content types"""
    VIDEO_SHORT = "video_short"      # TikTok, Reels, Shorts
    VIDEO_LONG = "video_long"        # YouTube long-form
    IMAGE_POST = "image_post"        # Instagram feed, Pinterest
    IMAGE_STORY = "image_story"      # Stories format
    TEXT_POST = "text_post"          # Twitter, LinkedIn
    AUDIO_CLIP = "audio_clip"        # Podcast clips, audio memes
    CAROUSEL = "carousel"            # Multi-image posts
    LIVE_STREAM = "live_stream"      # Live content


class Platform(Enum):
    """Social media platforms"""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"


class EngagementMetric(Enum):
    """Engagement metric types"""
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    WATCH_TIME = "watch_time"
    COMPLETION_RATE = "completion_rate"


@dataclass
class ContentMetadata:
    """Metadata for content pieces"""
    title: str = "Untitled Content"
    description: str = "AI-generated content"
    tags: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    location: Optional[str] = None
    language: str = "en"
    category: Optional[str] = None
    is_sponsored: bool = False
    sponsor_info: Optional[Dict[str, Any]] = None
    
    # SEO and discovery
    keywords: List[str] = field(default_factory=list)
    thumbnail_url: Optional[str] = None
    
    # Timing
    publish_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None


@dataclass
class ConsciousnessParameters:
    """Consciousness modeling parameters for content"""
    chakra_alignment: Dict[str, float] = field(default_factory=dict)
    fractal_dimension: float = 1.618  # φ
    phi_resonance: float = 0.0
    emotional_spectrum: Dict[str, float] = field(default_factory=dict)
    coherence_level: float = 0.7
    vibrational_signature: Optional[List[float]] = None


@dataclass
class OptimizationMetrics:
    """Metrics for content optimization"""
    predicted_engagement: float = 0.0
    viral_coefficient: float = 0.0
    roi_estimate: float = 0.0
    target_audience_match: float = 0.0
    trend_alignment: float = 0.0
    platform_optimization_score: float = 0.0
    
    # Performance tracking
    actual_engagement: Optional[float] = None
    performance_delta: Optional[float] = None


@dataclass
class ContentPiece:
    """Core content piece data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_type: ContentType = ContentType.VIDEO_SHORT
    platform: Platform = Platform.TIKTOK
    
    # Content data
    raw_content: Any = None  # Could be video bytes, image, text, etc.
    processed_content: Optional[Any] = None
    content_url: Optional[str] = None
    
    # Metadata
    metadata: ContentMetadata = field(default_factory=ContentMetadata)
    
    # Consciousness modeling
    consciousness: ConsciousnessParameters = field(default_factory=ConsciousnessParameters)
    
    # Optimization
    optimization: OptimizationMetrics = field(default_factory=OptimizationMetrics)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Analytics
    engagement_data: Dict[EngagementMetric, float] = field(default_factory=dict)
    revenue_generated: float = 0.0
    
    # Status
    status: str = "draft"  # draft, processing, scheduled, published, archived
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "content_type": self.content_type.value,
            "platform": self.platform.value,
            "metadata": {
                "title": self.metadata.title,
                "description": self.metadata.description,
                "tags": self.metadata.tags,
                "hashtags": self.metadata.hashtags,
            },
            "consciousness": {
                "fractal_dimension": self.consciousness.fractal_dimension,
                "coherence_level": self.consciousness.coherence_level,
            },
            "optimization": {
                "predicted_engagement": self.optimization.predicted_engagement,
                "viral_coefficient": self.optimization.viral_coefficient,
            },
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


@dataclass
class ContentBatch:
    """Batch of related content pieces"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    campaign_name: Optional[str] = None
    content_pieces: List[ContentPiece] = field(default_factory=list)
    
    # Batch-level optimization
    cross_platform_synergy: float = 0.0
    campaign_coherence: float = 0.0
    
    # Timing
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    def add_content(self, content: ContentPiece):
        """Add content piece to batch"""
        self.content_pieces.append(content)
    
    def get_by_platform(self, platform: Platform) -> List[ContentPiece]:
        """Get all content for a specific platform"""
        return [c for c in self.content_pieces if c.platform == platform]
    
    def calculate_synergy(self):
        """Calculate cross-platform synergy score"""
        if len(self.content_pieces) < 2:
            self.cross_platform_synergy = 0.0
            return
        
        # Calculate based on consciousness coherence
        coherences = [c.consciousness.coherence_level for c in self.content_pieces]
        avg_coherence = sum(coherences) / len(coherences)
        
        # Factor in platform diversity
        platforms = len(set(c.platform for c in self.content_pieces))
        diversity_bonus = min(platforms / 3, 1.0) * 0.2
        
        self.cross_platform_synergy = avg_coherence + diversity_bonus


@dataclass
class ContentTemplate:
    """Reusable content template"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Template"
    content_type: ContentType = ContentType.VIDEO_SHORT
    platform: Platform = Platform.TIKTOK
    
    # Template structure
    structure: Dict[str, Any] = field(default_factory=dict)
    
    # Default parameters
    default_consciousness: ConsciousnessParameters = field(default_factory=ConsciousnessParameters)
    
    # Performance history
    avg_engagement_rate: float = 0.0
    times_used: int = 0
    total_revenue: float = 0.0
    
    def apply_to_content(self, content_data: Dict[str, Any]) -> ContentPiece:
        """Apply template to create new content piece"""
        content = ContentPiece(
            content_type=self.content_type,
            platform=self.platform,
            consciousness=ConsciousnessParameters(**vars(self.default_consciousness))
        )
        
        # Apply template structure
        # This would be implemented based on specific template types
        
        self.times_used += 1
        return content