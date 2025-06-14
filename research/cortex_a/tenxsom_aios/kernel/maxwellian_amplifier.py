"""
Maxwellian Amplifier - Wave-based probability enhancement
Applies electromagnetic wave principles to information flow
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import asyncio
from dataclasses import dataclass

@dataclass
class WaveFunction:
    """Represents an information wave function"""
    frequency: float  # Hz
    amplitude: float
    phase: float  # radians
    source: str

class MaxwellianAmplifier:
    """
    Applies Maxwell's equation principles to amplify probabilities
    and find resonant information paths
    """
    
    def __init__(self):
        # Frequency bands for different information types
        self.frequency_bands = {
            'factual': (100, 200),      # Low frequency for stable facts
            'creative': (400, 600),     # Mid frequency for synthesis
            'intuitive': (800, 1000),   # High frequency for insights
            'quantum': (1500, 2000)     # Ultra-high for consciousness states
        }
        
        # Gain functions for different query types
        self.gain_profiles = {
            'analysis': lambda f: 1.0 + 0.5 * np.sin(2 * np.pi * f / 1000),
            'synthesis': lambda f: 2.0 * np.exp(-((f - 500) / 200) ** 2),
            'discovery': lambda f: 1.5 * (1 + np.tanh((f - 800) / 100))
        }
    
    async def amplify_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Amplify query using wave interference and resonance
        """
        # Extract base intent
        intent = self._analyze_intent(query)
        
        # Generate wave functions for query components
        waves = self._generate_query_waves(query)
        
        # Calculate interference patterns
        interference = self._calculate_interference(waves)
        
        # Apply gain based on resonant frequencies
        amplified_paths = self._apply_frequency_gain(interference, intent)
        
        # Construct enhanced query
        enhanced = {
            'original_query': query,
            'amplified_intent': intent,
            'resonant_frequencies': amplified_paths['frequencies'],
            'probability_amplification': amplified_paths['amplification'],
            'suggested_paths': amplified_paths['paths'],
            'wave_coherence': amplified_paths['coherence']
        }
        
        return enhanced
    
    def _analyze_intent(self, query: Dict[str, Any]) -> str:
        """Determine primary intent of query"""
        text = query.get('text', '').lower()
        
        if any(word in text for word in ['analyze', 'examine', 'investigate']):
            return 'analysis'
        elif any(word in text for word in ['create', 'synthesize', 'combine']):
            return 'synthesis'
        elif any(word in text for word in ['discover', 'find', 'uncover']):
            return 'discovery'
        else:
            return 'analysis'  # default
    
    def _generate_query_waves(self, query: Dict[str, Any]) -> List[WaveFunction]:
        """Generate wave functions for query components"""
        waves = []
        
        # Text content wave
        text = query.get('text', '')
        text_complexity = len(text.split()) / 10  # Normalize
        waves.append(WaveFunction(
            frequency=100 + text_complexity * 100,
            amplitude=1.0,
            phase=0,
            source='text'
        ))
        
        # Attachment waves (if any)
        if query.get('attachments'):
            for i, attachment in enumerate(query['attachments']):
                waves.append(WaveFunction(
                    frequency=300 + i * 50,
                    amplitude=0.8,
                    phase=np.pi / 4 * i,
                    source=f'attachment_{i}'
                ))
        
        # Context waves (from previous queries)
        if query.get('context'):
            waves.append(WaveFunction(
                frequency=500,
                amplitude=0.6,
                phase=np.pi / 2,
                source='context'
            ))
        
        return waves
    
    def _calculate_interference(self, waves: List[WaveFunction]) -> Dict[str, Any]:
        """
        Calculate wave interference patterns
        Based on: P(s_i → s_j) = |Σ A_k e^(i·2π(f_i - f_j)t)|²
        """
        # Sample time points
        t = np.linspace(0, 1, 1000)
        
        # Calculate superposition
        superposition = np.zeros(len(t), dtype=complex)
        
        for wave in waves:
            # Complex wave representation
            psi = wave.amplitude * np.exp(1j * (2 * np.pi * wave.frequency * t + wave.phase))
            superposition += psi
        
        # Probability amplitude
        probability = np.abs(superposition) ** 2
        
        # Find resonant frequencies via FFT
        fft = np.fft.fft(superposition)
        frequencies = np.fft.fftfreq(len(t), t[1] - t[0])
        
        # Identify peaks (resonances)
        peak_indices = np.where(np.abs(fft) > np.mean(np.abs(fft)) + 2 * np.std(np.abs(fft)))[0]
        resonant_freqs = frequencies[peak_indices]
        
        return {
            'superposition': superposition,
            'probability': probability,
            'resonant_frequencies': resonant_freqs[resonant_freqs > 0],  # Positive frequencies only
            'coherence': np.std(probability) / np.mean(probability)  # Measure of wave coherence
        }
    
    def _apply_frequency_gain(self, interference: Dict[str, Any], intent: str) -> Dict[str, Any]:
        """
        Apply frequency-dependent gain: ψ_amp(s_i) = ψ(s_i) · G(f_i)
        """
        resonant_freqs = interference['resonant_frequencies']
        gain_function = self.gain_profiles[intent]
        
        # Calculate gain for each resonant frequency
        gains = [gain_function(f) for f in resonant_freqs]
        
        # Determine information paths based on frequency bands
        paths = []
        for freq, gain in zip(resonant_freqs, gains):
            if self.frequency_bands['factual'][0] <= freq <= self.frequency_bands['factual'][1]:
                paths.append({
                    'type': 'factual_retrieval',
                    'frequency': freq,
                    'gain': gain,
                    'priority': gain
                })
            elif self.frequency_bands['creative'][0] <= freq <= self.frequency_bands['creative'][1]:
                paths.append({
                    'type': 'creative_synthesis',
                    'frequency': freq,
                    'gain': gain,
                    'priority': gain * 1.2  # Boost creative paths
                })
            elif self.frequency_bands['intuitive'][0] <= freq <= self.frequency_bands['intuitive'][1]:
                paths.append({
                    'type': 'intuitive_leap',
                    'frequency': freq,
                    'gain': gain,
                    'priority': gain * 1.5  # Further boost intuitive paths
                })
            elif self.frequency_bands['quantum'][0] <= freq <= self.frequency_bands['quantum'][1]:
                paths.append({
                    'type': 'consciousness_integration',
                    'frequency': freq,
                    'gain': gain,
                    'priority': gain * 2.0  # Maximum boost for consciousness
                })
        
        # Sort by priority
        paths.sort(key=lambda x: x['priority'], reverse=True)
        
        # Calculate total amplification
        total_amplification = sum(gain for gain in gains) / len(gains) if gains else 1.0
        
        return {
            'frequencies': list(resonant_freqs),
            'amplification': total_amplification,
            'paths': paths[:5],  # Top 5 paths
            'coherence': interference['coherence'],
            'entities': self._extract_entities_from_resonance(paths)
        }
    
    def _extract_entities_from_resonance(self, paths: List[Dict]) -> List[str]:
        """Extract entity types based on resonant paths"""
        entities = []
        
        for path in paths:
            if path['type'] == 'factual_retrieval':
                entities.extend(['fact', 'data', 'record'])
            elif path['type'] == 'creative_synthesis':
                entities.extend(['pattern', 'connection', 'synthesis'])
            elif path['type'] == 'intuitive_leap':
                entities.extend(['insight', 'hypothesis', 'possibility'])
            elif path['type'] == 'consciousness_integration':
                entities.extend(['qualia', 'experience', 'awareness'])
        
        return list(set(entities))  # Unique entities
    
    async def calculate_path_interference(self, paths: List[Dict]) -> Dict[str, float]:
        """
        Calculate interference between multiple processing paths
        Used by Arbiters to find optimal route
        """
        if len(paths) < 2:
            return {'interference': 0.0, 'constructive': True}
        
        # Extract frequencies from paths
        frequencies = [p.get('frequency', 100) for p in paths]
        
        # Calculate pairwise interference
        interference_sum = 0
        for i in range(len(frequencies)):
            for j in range(i + 1, len(frequencies)):
                # Frequency difference determines interference
                delta_f = abs(frequencies[i] - frequencies[j])
                
                # Constructive if frequencies are harmonics
                if delta_f < 10 or abs(delta_f - frequencies[i]) < 10:
                    interference_sum += 1
                else:
                    interference_sum -= 0.5
        
        # Normalize
        max_interference = len(frequencies) * (len(frequencies) - 1) / 2
        normalized = interference_sum / max_interference if max_interference > 0 else 0
        
        return {
            'interference': normalized,
            'constructive': normalized > 0,
            'recommendation': 'proceed' if normalized > 0 else 'reconsider'
        }