#!/usr/bin/env python3
"""
Test script for Frame Pack video generation
"""

import logging
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Add prostudio to path
sys.path.insert(0, str(Path(__file__).parent))

from prostudio_tools.video_gen import FramePackGenerator, VideoGenerationConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_image(path: Path, size=(512, 512)):
    """Create a test image with gradient"""
    width, height = size
    # Create a gradient image
    x = np.linspace(0, 255, width)
    y = np.linspace(0, 255, height)
    xv, yv = np.meshgrid(x, y)
    
    # Create RGB channels
    r = xv.astype(np.uint8)
    g = yv.astype(np.uint8)
    b = ((xv + yv) / 2).astype(np.uint8)
    
    # Stack into RGB image
    img_array = np.stack([r, g, b], axis=-1)
    img = Image.fromarray(img_array)
    
    # Add some text
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    text = "ProStudio Test"
    # Use default font
    draw.text((width//2 - 50, height//2), text, fill=(255, 255, 255))
    
    img.save(path)
    logger.info(f"Created test image: {path}")


def test_framepack_generation():
    """Test Frame Pack video generation"""
    logger.info("Starting Frame Pack test...")
    
    # Create test image
    test_image_path = Path("test_input.png")
    create_test_image(test_image_path)
    
    # Initialize generator
    generator = FramePackGenerator()
    
    # Configure generation
    config = VideoGenerationConfig(
        num_frames=16,  # Short test video
        fps=8,
        width=512,
        height=512,
        guidance_scale=7.5,
        num_inference_steps=20  # Fewer steps for testing
    )
    
    # Test prompts
    prompts = [
        "A serene landscape with gentle wind blowing",
        "Abstract colors flowing and morphing smoothly",
        "Technology visualization with data streams"
    ]
    
    for i, prompt in enumerate(prompts):
        logger.info(f"\n--- Test {i+1}: {prompt} ---")
        
        try:
            # Generate video
            result = generator.generate_from_image(
                image_path=test_image_path,
                prompt=prompt,
                config=config
            )
            
            # Check result
            if result.video_path.exists():
                file_size = result.video_path.stat().st_size / 1024 / 1024  # MB
                logger.info(f"✓ Video generated successfully: {result.video_path}")
                logger.info(f"  File size: {file_size:.2f} MB")
                logger.info(f"  Generation time: {result.generation_time:.2f}s")
                logger.info(f"  Memory used: {result.memory_used:.2f} GB")
            else:
                logger.error(f"✗ Video file not created")
                
        except Exception as e:
            logger.error(f"✗ Generation failed: {e}")
            
    # Test text-to-video (which internally uses image-to-video)
    logger.info("\n--- Testing text-to-video ---")
    try:
        result = generator.generate_from_text(
            prompt="A futuristic city with flying cars",
            config=config
        )
        logger.info(f"✓ Text-to-video successful: {result.video_path}")
    except Exception as e:
        logger.error(f"✗ Text-to-video failed: {e}")
        
    # Cleanup
    generator.unload_model()
    logger.info("\nTest complete!")
    

if __name__ == "__main__":
    test_framepack_generation()