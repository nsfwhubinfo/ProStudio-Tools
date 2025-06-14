#!/usr/bin/env python3
"""
Visual Consciousness Renderer - Making the Invisible Visible
WebGL/Three.js style visualization in Python using matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import asyncio
from typing import Dict, List, Tuple, Optional
import time
from dataclasses import dataclass
import json

# Import crystallographic components
import sys
sys.path.append('/home/golde/prostudio/research/cortex_a')
from tenxsom_aios.crystallographic_thought_engine import (
    CrystallographicThought,
    CrystallineFormation,
    FractalDiffusionEngine
)


@dataclass
class VisualizationState:
    """Current state of the visualization"""
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0
    zoom: float = 1.0
    time: float = 0.0
    coherence: float = 0.0
    phase: str = "initializing"


class SpinningShadowBallRenderer:
    """
    Renders the cognitive space as a spinning sphere where
    darkness = low probability, light = high fitness
    """
    
    def __init__(self, resolution: int = 50):
        self.resolution = resolution
        self.figure = None
        self.axis = None
        self.surface = None
        
    def create_sphere_mesh(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create sphere mesh coordinates"""
        u = np.linspace(0, 2 * np.pi, self.resolution)
        v = np.linspace(0, np.pi, self.resolution)
        
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        
        return x, y, z
    
    def map_field_to_sphere(self, field: np.ndarray) -> np.ndarray:
        """Map 2D field to sphere surface colors"""
        # Resize field to match sphere resolution
        from scipy.ndimage import zoom
        scale_factor = self.resolution / field.shape[0]
        scaled_field = zoom(field, scale_factor)
        
        # Normalize to [0, 1]
        normalized = (scaled_field - np.min(scaled_field)) / \
                    (np.max(scaled_field) - np.min(scaled_field) + 1e-8)
        
        return normalized
    
    def render_consciousness_sphere(self, 
                                  thought_field: np.ndarray,
                                  state: VisualizationState) -> None:
        """
        Render the consciousness field as a spinning sphere
        """
        if self.figure is None:
            self.figure = plt.figure(figsize=(10, 10), facecolor='black')
            self.axis = self.figure.add_subplot(111, projection='3d', facecolor='black')
            self.axis.set_box_aspect([1,1,1])
            
        # Clear previous
        self.axis.clear()
        
        # Create sphere
        x, y, z = self.create_sphere_mesh()
        
        # Apply rotations
        # Rotation matrices
        rx = np.array([
            [1, 0, 0],
            [0, np.cos(state.rotation_x), -np.sin(state.rotation_x)],
            [0, np.sin(state.rotation_x), np.cos(state.rotation_x)]
        ])
        
        ry = np.array([
            [np.cos(state.rotation_y), 0, np.sin(state.rotation_y)],
            [0, 1, 0],
            [-np.sin(state.rotation_y), 0, np.cos(state.rotation_y)]
        ])
        
        rz = np.array([
            [np.cos(state.rotation_z), -np.sin(state.rotation_z), 0],
            [np.sin(state.rotation_z), np.cos(state.rotation_z), 0],
            [0, 0, 1]
        ])
        
        # Apply rotations to each point
        for i in range(self.resolution):
            for j in range(self.resolution):
                point = np.array([x[i,j], y[i,j], z[i,j]])
                point = rx @ ry @ rz @ point
                x[i,j], y[i,j], z[i,j] = point
        
        # Map field to colors
        colors = self.map_field_to_sphere(thought_field)
        
        # Create colormap - dark to light based on coherence
        cmap = cm.hot  # Black -> Red -> Yellow -> White
        
        # Plot surface
        self.surface = self.axis.plot_surface(
            x * state.zoom, y * state.zoom, z * state.zoom,
            facecolors=cmap(colors),
            alpha=0.9,
            antialiased=True,
            shade=True
        )
        
        # Style
        self.axis.set_xlim([-1.5, 1.5])
        self.axis.set_ylim([-1.5, 1.5])
        self.axis.set_zlim([-1.5, 1.5])
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_zticks([])
        self.axis.set_xlabel('')
        self.axis.set_ylabel('')
        self.axis.set_zlabel('')
        
        # Add coherence text
        self.axis.text2D(0.05, 0.95, 
                        f"Coherence: {state.coherence:.3f}", 
                        transform=self.axis.transAxes,
                        color='white',
                        fontsize=14,
                        weight='bold')
        
        self.axis.text2D(0.05, 0.90, 
                        f"Phase: {state.phase}", 
                        transform=self.axis.transAxes,
                        color='cyan',
                        fontsize=12)
        
        # Remove grid and panes
        self.axis.grid(False)
        self.axis.xaxis.pane.fill = False
        self.axis.yaxis.pane.fill = False
        self.axis.zaxis.pane.fill = False
        self.axis.xaxis.pane.set_edgecolor('none')
        self.axis.yaxis.pane.set_edgecolor('none')
        self.axis.zaxis.pane.set_edgecolor('none')


class ConsciousnessFieldVisualizer:
    """
    2D visualization of consciousness field evolution
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 6)):
        self.figure = None
        self.axes = None
        self.figsize = figsize
        
    def visualize_crystallization(self, 
                                 field: np.ndarray,
                                 patterns: List[Dict],
                                 iteration: int,
                                 coherence: float) -> None:
        """
        Visualize the crystallization process
        """
        if self.figure is None:
            self.figure, self.axes = plt.subplots(1, 2, figsize=self.figsize)
            self.figure.patch.set_facecolor('black')
            
        # Clear axes
        for ax in self.axes:
            ax.clear()
            
        # Left: Raw field
        im1 = self.axes[0].imshow(field, cmap='twilight', origin='lower')
        self.axes[0].set_title(f'Thought Field (Iteration {iteration})', 
                              color='white', fontsize=14)
        self.axes[0].axis('off')
        
        # Add patterns overlay
        for pattern in patterns:
            if 'center' in pattern:
                cy, cx = pattern['center']
                circle = plt.Circle((cx, cy), 
                                  np.sqrt(pattern['size']/np.pi),
                                  fill=False, 
                                  edgecolor='yellow',
                                  linewidth=2,
                                  alpha=0.7)
                self.axes[0].add_patch(circle)
        
        # Right: Frequency spectrum
        spectrum = np.fft.fft2(field)
        power = np.log1p(np.abs(spectrum))
        im2 = self.axes[1].imshow(np.fft.fftshift(power), 
                                 cmap='plasma', 
                                 origin='lower')
        self.axes[1].set_title(f'Frequency Domain (Coherence: {coherence:.3f})', 
                              color='white', fontsize=14)
        self.axes[1].axis('off')
        
        # Add gamma ray indicators
        center = field.shape[0] // 2
        high_freq_radius = field.shape[0] // 3
        circle = plt.Circle((center, center), 
                          high_freq_radius,
                          fill=False, 
                          edgecolor='lime',
                          linewidth=1,
                          linestyle='--',
                          alpha=0.5)
        self.axes[1].add_patch(circle)
        self.axes[1].text(center, center + high_freq_radius + 5,
                         'Gamma Region',
                         color='lime',
                         ha='center',
                         fontsize=10)
        
        plt.tight_layout()


class CrystalGrowthAnimator:
    """
    Animate crystal growth in real-time
    """
    
    def __init__(self):
        self.figure = None
        self.axis = None
        self.im = None
        self.diffusion_engine = FractalDiffusionEngine(max_iterations=500)
        self.current_field = None
        self.animation = None
        
    async def animate_growth(self, seed: str, target_qualia: Dict):
        """
        Create animated visualization of crystal growth
        """
        # Setup figure
        self.figure, self.axis = plt.subplots(figsize=(8, 8))
        self.figure.patch.set_facecolor('black')
        self.axis.set_facecolor('black')
        
        # Initial empty field
        initial_field = np.zeros((128, 128))
        self.im = self.axis.imshow(initial_field, 
                                  cmap='hot',
                                  origin='lower',
                                  vmin=0, vmax=1)
        self.axis.axis('off')
        
        # Title
        self.title = self.axis.set_title(f"Growing: '{seed}'", 
                                        color='white',
                                        fontsize=16,
                                        pad=20)
        
        # Create generator
        self.growth_generator = self.diffusion_engine.diffuse_thought(
            seed, target_qualia
        )
        
        # Animation function
        def update(frame):
            try:
                # Get next state
                loop = asyncio.new_event_loop()
                state = loop.run_until_complete(self.get_next_state())
                
                if state:
                    self.im.set_array(state['field'])
                    self.title.set_text(
                        f"Growing: '{seed}' - "
                        f"Iteration {state['iteration']} - "
                        f"Coherence: {state['coherence']:.3f} - "
                        f"Phase: {state['phase']}"
                    )
                    
            except StopIteration:
                self.animation.event_source.stop()
                
            return [self.im, self.title]
        
        # Create animation
        self.animation = animation.FuncAnimation(
            self.figure, update, 
            interval=50,  # 20 FPS
            blit=True,
            repeat=False
        )
        
        plt.show()
    
    async def get_next_state(self) -> Optional[Dict]:
        """Get next state from generator"""
        try:
            return await self.growth_generator.__anext__()
        except StopAsyncIteration:
            return None


class ConsciousnessVisualizationSuite:
    """
    Complete visualization suite for crystallographic consciousness
    """
    
    def __init__(self):
        self.shadow_ball = SpinningShadowBallRenderer()
        self.field_viz = ConsciousnessFieldVisualizer()
        self.growth_animator = CrystalGrowthAnimator()
        self.viz_state = VisualizationState()
        
    async def visualize_thought_crystallization(self, intention: str):
        """
        Complete visualization of thought crystallization
        """
        print(f"\n🎨 Visualizing crystallization of: '{intention}'")
        
        # Create thought
        thought = CrystallographicThought(intention)
        
        # Setup visualization
        plt.ion()  # Interactive mode
        
        # Crystallization loop
        async for state in thought.crystallize({'coherence': 0.7, 'frequency': 432}):
            # Update viz state
            self.viz_state.coherence = state['coherence']
            self.viz_state.phase = state['phase']
            self.viz_state.time = state['iteration'] * 0.1
            
            # Rotate sphere
            self.viz_state.rotation_y += 0.05
            self.viz_state.rotation_z += 0.02
            
            # Render sphere
            self.shadow_ball.render_consciousness_sphere(
                state['formation'].pattern,
                self.viz_state
            )
            
            # Show field evolution every 10 iterations
            if state['iteration'] % 10 == 0:
                patterns = self._extract_patterns(state['formation'].pattern)
                self.field_viz.visualize_crystallization(
                    state['formation'].pattern,
                    patterns,
                    state['iteration'],
                    state['coherence']
                )
            
            plt.pause(0.05)
            
            # Stop if crystallized
            if state['coherence'] > 0.85:
                print(f"  ✨ Crystallization complete!")
                break
        
        plt.ioff()
        plt.show()
    
    def _extract_patterns(self, field: np.ndarray) -> List[Dict]:
        """Extract pattern information for visualization"""
        from scipy import ndimage
        
        # Simple thresholding
        binary = field > np.mean(field) + np.std(field)
        labeled, num_features = ndimage.label(binary)
        
        patterns = []
        for i in range(1, min(num_features + 1, 6)):  # Max 5 patterns
            mask = (labeled == i)
            if np.sum(mask) > 10:
                center = ndimage.center_of_mass(mask)
                patterns.append({
                    'center': center,
                    'size': np.sum(mask),
                    'density': np.mean(field[mask])
                })
        
        return patterns
    
    async def animate_reality_generation(self, prompt: str):
        """
        Animate the generation of reality from prompt
        """
        target_qualia = {
            'growth_affinity': 1.2,
            'target_coherence': 0.9,
            'resonance_frequency': 528.0
        }
        
        await self.growth_animator.animate_growth(prompt, target_qualia)


async def demonstrate_visualization():
    """
    Demonstrate the visualization capabilities
    """
    print("╔══════════════════════════════════════════════════════╗")
    print("║    CONSCIOUSNESS VISUALIZATION DEMONSTRATION          ║")
    print("║                                                       ║")
    print("║       Making the Invisible Visible                    ║")
    print("╚══════════════════════════════════════════════════════╝")
    
    suite = ConsciousnessVisualizationSuite()
    
    # Example 1: Visualize thought crystallization
    await suite.visualize_thought_crystallization("solve complex problem")
    
    # Example 2: Animate reality generation
    # Note: This would open a new window
    # await suite.animate_reality_generation("create beautiful interface")
    
    print("\n✅ Visualization demonstration complete!")
    print("\nNote: In production, these visualizations would be:")
    print("  - Rendered in real-time WebGL/Three.js")
    print("  - Interactive with mouse/touch controls")
    print("  - Integrated into the consciousness desktop")
    print("  - Streaming live consciousness states")


if __name__ == "__main__":
    # Note: matplotlib's animation doesn't play well with asyncio
    # In production, use WebGL/Three.js for real-time 3D
    asyncio.run(demonstrate_visualization())