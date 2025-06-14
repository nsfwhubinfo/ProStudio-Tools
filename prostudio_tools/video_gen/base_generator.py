"""
Base class for video generation models
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import torch
import logging
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class VideoGenerationConfig:
    """Configuration for video generation"""
    num_frames: int = 16
    fps: int = 8
    width: int = 512
    height: int = 512
    guidance_scale: float = 7.5
    num_inference_steps: int = 50
    seed: Optional[int] = None
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    dtype: torch.dtype = torch.float16
    
    
@dataclass
class VideoGenerationResult:
    """Result of video generation"""
    video_path: Path
    metadata: Dict
    generation_time: float
    memory_used: float  # in GB
    

class BaseVideoGenerator(ABC):
    """Abstract base class for video generation models"""
    
    def __init__(self, model_name: str, cache_dir: Optional[Path] = None):
        self.model_name = model_name
        self.cache_dir = cache_dir or Path.home() / ".cache" / "prostudio" / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    @abstractmethod
    def load_model(self) -> None:
        """Load the model weights"""
        pass
        
    @abstractmethod
    def generate_from_text(
        self, 
        prompt: str, 
        config: VideoGenerationConfig,
        output_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        """Generate video from text prompt"""
        pass
        
    @abstractmethod
    def generate_from_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        config: VideoGenerationConfig,
        output_path: Optional[Path] = None
    ) -> VideoGenerationResult:
        """Generate video from image and prompt"""
        pass
        
    def unload_model(self) -> None:
        """Unload model from memory"""
        if self.model is not None:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info(f"Unloaded {self.model_name} from memory")
            
    def get_memory_usage(self) -> float:
        """Get current GPU memory usage in GB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**3
        return 0.0
        
    def log_generation_stats(self, result: VideoGenerationResult) -> None:
        """Log generation statistics"""
        logger.info(f"Generated video: {result.video_path}")
        logger.info(f"Generation time: {result.generation_time:.2f}s")
        logger.info(f"Memory used: {result.memory_used:.2f}GB")
        logger.info(f"Metadata: {result.metadata}")