# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: cdivision=True
"""
Cython-optimized Consciousness Metrics Calculations
==================================================

Ultra-fast consciousness scoring and resonance calculations.
"""

import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport exp, pow, sqrt, cos, sin, log, fabs

# Type definitions
ctypedef np.float64_t DOUBLE
ctypedef np.float32_t FLOAT
ctypedef np.int64_t INT64

# Constants
cdef double PHI = 1.618033988749895
cdef double INV_PHI = 0.618033988749895
cdef double PI = 3.141592653589793


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_phi_resonance_fast(double[:] frequencies, double[:] amplitudes):
    """
    Ultra-fast φ resonance calculation
    
    Args:
        frequencies: Array of frequencies
        amplitudes: Array of amplitudes
        
    Returns:
        φ resonance score
    """
    cdef int i, n = frequencies.shape[0]
    cdef double resonance = 0.0
    cdef double freq, amp
    cdef double harmonic_sum = 0.0
    
    # Key φ harmonic frequencies
    cdef double[7] phi_harmonics = [256.0, 341.3, 426.7, 512.0, 640.0, 768.0, 853.3]
    cdef double[7] harmonic_weights = [1.0, PHI, PHI*PHI, INV_PHI, PHI/2, INV_PHI/2, PHI*PHI*PHI]
    
    for i in range(n):
        freq = frequencies[i]
        amp = amplitudes[i]
        
        # Calculate resonance with each φ harmonic
        for j in range(7):
            # Gaussian resonance curve
            harmonic_sum += amp * harmonic_weights[j] * exp(-pow((freq / phi_harmonics[j] - 1.0), 2) / 0.1)
    
    resonance = harmonic_sum / (n * 7.0)
    
    # Clip to [0, 1]
    if resonance > 1.0:
        resonance = 1.0
    elif resonance < 0.0:
        resonance = 0.0
    
    return resonance


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double calculate_coherence_matrix_fast(double[:, :] chakra_states):
    """
    Fast coherence matrix calculation
    
    Args:
        chakra_states: 2D array [n_chakras, features]
        
    Returns:
        Average coherence score
    """
    cdef int i, j
    cdef int n = chakra_states.shape[0]
    cdef double total_coherence = 0.0
    cdef int count = 0
    
    cdef double phase_i, phase_j, amp_i, amp_j
    cdef double phase_coherence, amp_coherence
    
    # Pairwise coherence calculation
    for i in range(n):
        for j in range(i + 1, n):
            # Extract features (assuming: phase, amplitude, frequency)
            phase_i = chakra_states[i, 0]
            phase_j = chakra_states[j, 0]
            amp_i = chakra_states[i, 1]
            amp_j = chakra_states[j, 1]
            
            # Phase coherence
            phase_coherence = cos(phase_i - phase_j)
            
            # Amplitude coherence
            amp_coherence = 1.0 - fabs(amp_i - amp_j)
            
            # Combined coherence
            total_coherence += (phase_coherence + amp_coherence) / 2.0
            count += 1
    
    if count > 0:
        return total_coherence / count
    else:
        return 0.5


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_consciousness_score_fast(
    double fractal_dimension,
    double phi_resonance,
    double coherence_level,
    double[:] emotional_spectrum
):
    """
    Fast consciousness score calculation
    
    Args:
        fractal_dimension: Fractal dimension value
        phi_resonance: φ resonance score
        coherence_level: Coherence level
        emotional_spectrum: Array of emotional values
        
    Returns:
        Consciousness score (0-100)
    """
    cdef double score = 0.0
    cdef double phi_proximity = 1.0 - fabs(fractal_dimension - PHI) / PHI
    cdef double emotional_charge = 0.0
    cdef int i, n = emotional_spectrum.shape[0]
    
    # Calculate emotional charge
    if n > 0:
        for i in range(n):
            emotional_charge += emotional_spectrum[i]
        emotional_charge /= n
    else:
        emotional_charge = 0.5
    
    # Weighted combination
    score = (
        phi_proximity * 0.3 +
        phi_resonance * 0.3 +
        coherence_level * 0.25 +
        emotional_charge * 0.15
    ) * 100.0
    
    # Ensure bounds
    if score > 100.0:
        score = 100.0
    elif score < 0.0:
        score = 0.0
    
    return score


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double calculate_viral_potential_fast(
    double engagement_rate,
    double consciousness_score,
    int platform_id,
    int content_type_id
):
    """
    Fast viral potential calculation
    
    Args:
        engagement_rate: Predicted engagement rate
        consciousness_score: Consciousness score
        platform_id: Platform identifier (0=TikTok, 1=Instagram, 2=YouTube)
        content_type_id: Content type identifier
        
    Returns:
        Viral coefficient
    """
    cdef double viral_coefficient = 1.0
    
    # Platform multipliers
    cdef double[3] platform_multipliers = [1.3, 1.1, 1.0]  # TikTok, Instagram, YouTube
    
    # Content type multipliers
    cdef double[4] content_multipliers = [1.2, 1.0, 0.9, 1.1]  # Video short, image, video long, carousel
    
    # Base calculation
    viral_coefficient = (engagement_rate / 100.0) * (consciousness_score / 100.0)
    
    # Apply multipliers
    if 0 <= platform_id < 3:
        viral_coefficient *= platform_multipliers[platform_id]
    
    if 0 <= content_type_id < 4:
        viral_coefficient *= content_multipliers[content_type_id]
    
    # Consciousness boost
    if consciousness_score > 80:
        viral_coefficient *= 1.2
    elif consciousness_score > 60:
        viral_coefficient *= 1.1
    
    # Apply golden ratio scaling
    viral_coefficient *= pow(PHI, viral_coefficient / 2.0 - 0.5)
    
    return viral_coefficient


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef void batch_calculate_metrics(
    double[:, :] consciousness_data,
    double[:] results,
    int n_samples
):
    """
    Batch calculate consciousness metrics
    
    Args:
        consciousness_data: 2D array of consciousness parameters [n_samples, n_features]
        results: Output array for results [n_samples * 4] (score, resonance, coherence, viral)
        n_samples: Number of samples
    """
    cdef int i
    cdef double fractal_dim, coherence, phi_res
    cdef double score, viral
    
    # Process each sample
    for i in range(n_samples):
        # Extract features (assuming fixed layout)
        fractal_dim = consciousness_data[i, 0]
        coherence = consciousness_data[i, 1]
        phi_res = consciousness_data[i, 2]
        
        # Calculate metrics
        score = calculate_consciousness_score_fast(
            fractal_dim, phi_res, coherence, 
            consciousness_data[i, 3:]  # Remaining features as emotional spectrum
        )
        
        viral = calculate_viral_potential_fast(
            score * 0.8 + 20,  # Convert to engagement rate
            score,
            <int>(consciousness_data[i, 1] * 3) % 3,  # Platform from coherence (hack)
            0  # Default content type
        )
        
        # Store results
        results[i * 4] = score
        results[i * 4 + 1] = phi_res
        results[i * 4 + 2] = coherence
        results[i * 4 + 3] = viral


# Python wrapper functions for easy use
def fast_consciousness_metrics(consciousness_params):
    """
    Python wrapper for fast consciousness calculations
    
    Args:
        consciousness_params: Dictionary with consciousness parameters
        
    Returns:
        Dictionary with calculated metrics
    """
    # Extract parameters
    frequencies = np.asarray(consciousness_params.get('frequencies', [256.0, 341.3, 512.0]), dtype=np.float64)
    amplitudes = np.asarray(consciousness_params.get('amplitudes', [0.7, 0.8, 0.6]), dtype=np.float64)
    fractal_dim = consciousness_params.get('fractal_dimension', 1.5)
    coherence = consciousness_params.get('coherence_level', 0.7)
    emotional_spectrum = np.asarray(consciousness_params.get('emotional_spectrum', [0.6, 0.7, 0.5]), dtype=np.float64)
    
    # Calculate metrics
    phi_resonance = calculate_phi_resonance_fast(frequencies, amplitudes)
    consciousness_score = calculate_consciousness_score_fast(
        fractal_dim, phi_resonance, coherence, emotional_spectrum
    )
    viral_potential = calculate_viral_potential_fast(
        consciousness_score * 0.8 + 20,  # Rough engagement estimate
        consciousness_score,
        0,  # TikTok default
        0   # Video short default
    )
    
    return {
        'phi_resonance': phi_resonance,
        'consciousness_score': consciousness_score,
        'viral_potential': viral_potential,
        'coherence_level': coherence
    }