#!/usr/bin/env python3
"""
ProStudio Quick Start
=====================

Get started with ProStudio in under 5 minutes!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.content_engine import ContentEngine, ContentType
from core.content_engine.content_types import Platform


def quickstart():
    """Quick start example"""
    print("🚀 ProStudio Quick Start")
    print("=" * 50)
    
    # 1. Initialize engine
    print("\n1️⃣ Initializing ProStudio...")
    engine = ContentEngine()
    engine.initialize()
    
    # 2. Generate your first content
    print("\n2️⃣ Generating your first viral content...")
    content = engine.generate_content(
        concept="How to make money with AI content",
        content_type=ContentType.VIDEO_SHORT,
        platform=Platform.TIKTOK
    )
    
    print(f"\n✅ Success! Generated content with:")
    print(f"   Predicted engagement: {content.optimization.predicted_engagement:.0f}%")
    print(f"   Viral coefficient: {content.optimization.viral_coefficient:.1f}x")
    print(f"   Consciousness score: {content.consciousness.coherence_level * 100:.0f}%")
    
    # 3. Generate multi-platform batch
    print("\n3️⃣ Generating multi-platform content batch...")
    batch = engine.generate_batch(
        concept="ProStudio creates content that sells itself",
        platforms=[Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE]
    )
    
    print(f"\n✅ Generated {len(batch.content_pieces)} pieces across platforms!")
    print(f"   Cross-platform synergy: {batch.cross_platform_synergy:.0%}")
    
    # 4. Show monetization potential
    print("\n💰 Monetization Potential:")
    total_reach = sum(c.optimization.predicted_engagement * c.optimization.viral_coefficient 
                     for c in batch.content_pieces)
    revenue_estimate = total_reach * 0.5  # $0.50 per 1% reach
    print(f"   Estimated reach score: {total_reach:.0f}")
    print(f"   Potential revenue: ${revenue_estimate:.0f}")
    
    print("\n🎉 You're ready to start creating viral content!")
    print("\n📚 Next steps:")
    print("   - Run demo_prostudio.py for full demo")
    print("   - Check examples/ folder for more templates")
    print("   - Read docs/ for API documentation")
    
    engine.shutdown()


if __name__ == "__main__":
    quickstart()