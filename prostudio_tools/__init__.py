"""
ProStudio Tools - Real implementations for content generation
"""

from pathlib import Path

# Tool directories
TOOLS_ROOT = Path(__file__).parent
VIDEO_GEN_DIR = TOOLS_ROOT / "video_gen"
AUDIO_GEN_DIR = TOOLS_ROOT / "audio_gen"
EDITING_DIR = TOOLS_ROOT / "editing"

# Output directories
OUTPUT_ROOT = Path(__file__).parent.parent / "outputs"
VIDEO_OUTPUT_DIR = OUTPUT_ROOT / "videos"
AUDIO_OUTPUT_DIR = OUTPUT_ROOT / "audio"
TEMP_DIR = OUTPUT_ROOT / "temp"

# Create directories if they don't exist
for dir_path in [VIDEO_OUTPUT_DIR, AUDIO_OUTPUT_DIR, TEMP_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

__version__ = "0.1.0"