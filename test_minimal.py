#!/usr/bin/env python3
"""
Minimal ProStudio Test
======================

Tests the actual content engine with minimal dependencies.
"""

import sys
import os
import time

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.content_engine import ContentEngine
    from core.content_types import Platform, ContentType
    
    print("✅ ProStudio modules loaded successfully!")
    
    # Create engine with minimal config
    print("\n🔧 Initializing content engine...")
    engine = ContentEngine({
        'enable_performance_mode': False,  # Disable advanced features
        'enable_fa_cms': False,            # Disable consciousness features
        'optimization_iterations': 1        # Minimal optimization
    })
    
    # Initialize
    engine.initialize()
    print("✅ Engine initialized!")
    
    # Test generation
    print("\n🚀 Testing content generation...")
    
    test_concepts = [
        "How to use AI for content creation",
        "Social media growth strategies",
        "Viral video secrets"
    ]
    
    for concept in test_concepts:
        print(f"\n📝 Generating: '{concept}'")
        
        start = time.time()
        try:
            content = engine.generate_content(
                concept=concept,
                content_type=ContentType.VIDEO_SHORT,
                platform=Platform.TIKTOK
            )
            
            duration = (time.time() - start) * 1000
            
            print(f"   ✓ Generated in {duration:.1f}ms")
            print(f"   📊 Engagement: {content.optimization.predicted_engagement:.1f}%")
            print(f"   🚀 Viral score: {content.optimization.viral_coefficient:.2f}x")
            
            # Show script preview
            if hasattr(content, 'metadata') and 'script' in content.metadata:
                script_preview = content.metadata['script'].split('\n')[0]
                print(f"   📝 Hook: {script_preview[:60]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Test complete!")
    print("\n💡 To see full features, install all dependencies:")
    print("   pip install -r requirements.txt")
    
except ImportError as e:
    print(f"❌ Error importing ProStudio modules: {e}")
    print("\nThis might be because some dependencies are missing.")
    print("The demo files show simulated output without dependencies.")
    print("\nTo see the actual engine in action:")
    print("1. Install basic dependencies:")
    print("   pip install numpy scipy scikit-learn")
    print("2. Then run this script again")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print("\nTry running the demo_sample.py for simulated output:")