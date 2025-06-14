# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: cdivision=True
"""
Cython-optimized Viral Scoring Engine
=====================================

Ultra-fast viral potential calculation and optimization.
"""

import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport exp, pow, log, sqrt, tanh, sin, cos
from libc.stdlib cimport rand, RAND_MAX

# Type definitions
ctypedef np.float64_t DOUBLE
ctypedef np.int32_t INT32
ctypedef np.uint64_t UINT64

# Constants
cdef double PHI = 1.618033988749895
cdef double E = 2.718281828459045
cdef double PI = 3.141592653589793

# Platform coefficients
cdef double[5] PLATFORM_COEFFICIENTS = [1.5, 1.2, 1.0, 1.3, 1.1]  # TikTok, Instagram, YouTube, Twitter, LinkedIn

# Content type multipliers
cdef double[5] CONTENT_MULTIPLIERS = [1.3, 1.0, 0.9, 1.2, 1.1]  # Video short, Image, Video long, Carousel, Story


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_engagement_score_fast(
    double[:] hashtag_scores,
    double[:] timing_factors,
    double emotional_intensity,
    int platform_id
):
    """
    Fast engagement score calculation
    
    Args:
        hashtag_scores: Array of hashtag relevance scores
        timing_factors: Array of timing optimization factors
        emotional_intensity: Emotional charge (0-1)
        platform_id: Platform identifier
        
    Returns:
        Engagement score (0-100)
    """
    cdef int i
    cdef int n_hashtags = hashtag_scores.shape[0]
    cdef int n_timing = timing_factors.shape[0]
    cdef double hashtag_impact = 0.0
    cdef double timing_impact = 0.0
    cdef double platform_mult = 1.0
    
    # Calculate hashtag impact
    if n_hashtags > 0:
        for i in range(n_hashtags):
            # Diminishing returns for too many hashtags
            hashtag_impact += hashtag_scores[i] * pow(0.85, i)
        hashtag_impact /= n_hashtags
    else:
        hashtag_impact = 0.3  # Baseline
    
    # Calculate timing impact
    if n_timing > 0:
        for i in range(n_timing):
            timing_impact += timing_factors[i]
        timing_impact /= n_timing
    else:
        timing_impact = 0.5
    
    # Platform multiplier
    if 0 <= platform_id < 5:
        platform_mult = PLATFORM_COEFFICIENTS[platform_id]
    
    # Combine factors
    cdef double engagement = (
        hashtag_impact * 0.3 +
        timing_impact * 0.25 +
        emotional_intensity * 0.35 +
        0.1  # Base engagement
    ) * platform_mult * 100.0
    
    # Apply sigmoid for realistic bounds
    engagement = 100.0 / (1.0 + exp(-0.1 * (engagement - 50.0)))
    
    return engagement


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_virality_coefficient_fast(
    double engagement_rate,
    double share_probability,
    double network_reach,
    double content_uniqueness
):
    """
    Fast virality coefficient calculation (K-factor)
    
    Args:
        engagement_rate: Predicted engagement rate (0-100)
        share_probability: Probability of sharing (0-1)
        network_reach: Average network size multiplier
        content_uniqueness: Uniqueness score (0-1)
        
    Returns:
        Virality coefficient (K-factor)
    """
    cdef double base_k = (engagement_rate / 100.0) * share_probability * network_reach
    
    # Apply uniqueness boost
    cdef double uniqueness_multiplier = 1.0 + content_uniqueness * PHI
    
    # Calculate K-factor with golden ratio scaling
    cdef double k_factor = base_k * uniqueness_multiplier
    
    # Apply non-linear scaling for viral potential
    if k_factor > 1.0:
        k_factor = 1.0 + log(k_factor) * PHI
    
    return k_factor


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double calculate_trend_alignment_fast(
    double[:] content_features,
    double[:] trend_features,
    double trend_velocity
):
    """
    Fast trend alignment calculation
    
    Args:
        content_features: Content feature vector
        trend_features: Current trend feature vector
        trend_velocity: Trend growth rate
        
    Returns:
        Trend alignment score (0-1)
    """
    cdef int i
    cdef int n_features = min(content_features.shape[0], trend_features.shape[0])
    cdef double cosine_sim = 0.0
    cdef double content_norm = 0.0
    cdef double trend_norm = 0.0
    
    # Calculate cosine similarity
    for i in range(n_features):
        cosine_sim += content_features[i] * trend_features[i]
        content_norm += content_features[i] * content_features[i]
        trend_norm += trend_features[i] * trend_features[i]
    
    if content_norm > 0 and trend_norm > 0:
        cosine_sim /= sqrt(content_norm * trend_norm)
    else:
        cosine_sim = 0.0
    
    # Apply trend velocity boost
    cdef double alignment = cosine_sim * (1.0 + trend_velocity * 0.5)
    
    # Clamp to [0, 1]
    if alignment > 1.0:
        alignment = 1.0
    elif alignment < 0.0:
        alignment = 0.0
    
    return alignment


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double optimize_posting_time_fast(
    double[:] historical_engagement,
    int target_hour,
    int target_day,
    int platform_id
):
    """
    Fast posting time optimization
    
    Args:
        historical_engagement: 24*7 array of historical engagement by hour/day
        target_hour: Target posting hour (0-23)
        target_day: Target day of week (0-6)
        platform_id: Platform identifier
        
    Returns:
        Optimal timing score (0-1)
    """
    cdef int hour, day
    cdef double score = 0.0
    cdef double weight
    cdef double distance
    cdef double platform_peak_hour = 0.0
    
    # Platform-specific peak hours
    if platform_id == 0:  # TikTok
        platform_peak_hour = 19.0  # 7 PM
    elif platform_id == 1:  # Instagram
        platform_peak_hour = 20.0  # 8 PM
    elif platform_id == 2:  # YouTube
        platform_peak_hour = 21.0  # 9 PM
    else:
        platform_peak_hour = 18.0  # 6 PM default
    
    # Calculate weighted score based on historical data
    for day in range(7):
        for hour in range(24):
            if day * 24 + hour < historical_engagement.shape[0]:
                # Distance-based weighting
                distance = sqrt(pow(hour - target_hour, 2) + pow((day - target_day) * 3, 2))
                weight = exp(-distance / 10.0)
                
                score += historical_engagement[day * 24 + hour] * weight
    
    # Normalize score
    score /= (7.0 * 24.0)
    
    # Apply platform peak hour bonus
    hour_distance = abs(target_hour - platform_peak_hour)
    peak_bonus = exp(-hour_distance / 4.0) * 0.2
    
    score = score * 0.8 + peak_bonus
    
    # Ensure bounds
    if score > 1.0:
        score = 1.0
    elif score < 0.0:
        score = 0.0
    
    return score


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_audience_resonance_fast(
    double[:] content_embedding,
    double[:] audience_embedding,
    double audience_size,
    double audience_engagement_rate
):
    """
    Fast audience resonance calculation
    
    Args:
        content_embedding: Content feature embedding
        audience_embedding: Target audience embedding
        audience_size: Size of target audience
        audience_engagement_rate: Historical engagement rate
        
    Returns:
        Audience resonance score
    """
    cdef int i
    cdef int n_dims = min(content_embedding.shape[0], audience_embedding.shape[0])
    cdef double similarity = 0.0
    cdef double content_energy = 0.0
    cdef double audience_energy = 0.0
    
    # Calculate embedding similarity
    for i in range(n_dims):
        similarity += content_embedding[i] * audience_embedding[i]
        content_energy += content_embedding[i] * content_embedding[i]
        audience_energy += audience_embedding[i] * audience_embedding[i]
    
    if content_energy > 0 and audience_energy > 0:
        similarity /= sqrt(content_energy * audience_energy)
    
    # Apply audience factors
    cdef double size_factor = log(audience_size + 1.0) / 20.0  # Logarithmic scaling
    if size_factor > 1.0:
        size_factor = 1.0
    
    cdef double resonance = similarity * size_factor * (0.5 + audience_engagement_rate / 200.0)
    
    return resonance


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.nogil
cdef double viral_growth_simulation_step(
    double current_views,
    double k_factor,
    double decay_rate,
    double external_boost
) nogil:
    """
    Single step of viral growth simulation (nogil for parallelization)
    """
    cdef double organic_growth = current_views * k_factor
    cdef double decay = current_views * decay_rate
    cdef double net_growth = organic_growth - decay + external_boost
    
    # Add some randomness for realism
    cdef double random_factor = (<double>rand() / RAND_MAX - 0.5) * 0.1
    net_growth *= (1.0 + random_factor)
    
    return current_views + net_growth


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double[:] simulate_viral_growth_fast(
    double initial_views,
    double k_factor,
    double decay_rate,
    int time_steps,
    double[:] external_boosts
):
    """
    Fast viral growth simulation
    
    Args:
        initial_views: Starting view count
        k_factor: Virality coefficient
        decay_rate: Content decay rate
        time_steps: Number of time steps to simulate
        external_boosts: Array of external boost values
        
    Returns:
        Array of view counts over time
    """
    cdef int t
    cdef double[:] views = np.zeros(time_steps, dtype=np.float64)
    cdef double current_views = initial_views
    cdef double boost
    
    views[0] = initial_views
    
    for t in range(1, time_steps):
        # Get external boost if available
        if t < external_boosts.shape[0]:
            boost = external_boosts[t]
        else:
            boost = 0.0
        
        # Simulate growth
        current_views = viral_growth_simulation_step(
            current_views, k_factor, decay_rate, boost
        )
        
        # Ensure non-negative
        if current_views < 0:
            current_views = 0
        
        views[t] = current_views
    
    return views


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef void batch_calculate_viral_scores(
    double[:, :] content_features,
    double[:] engagement_rates,
    int[:] platform_ids,
    double[:] results,
    int n_samples
):
    """
    Batch calculate viral scores for multiple contents
    
    Args:
        content_features: 2D array of content features [n_samples, n_features]
        engagement_rates: Array of engagement rates
        platform_ids: Array of platform IDs
        results: Output array for viral scores [n_samples * 3] (viral_score, k_factor, peak_views)
        n_samples: Number of samples
    """
    cdef int i
    cdef double viral_score, k_factor, peak_views
    cdef double uniqueness, share_prob, network_reach
    
    for i in range(n_samples):
        # Extract features (assuming layout: uniqueness, emotional_intensity, trend_alignment, ...)
        uniqueness = content_features[i, 0] if content_features.shape[1] > 0 else 0.7
        share_prob = content_features[i, 1] if content_features.shape[1] > 1 else 0.15
        network_reach = content_features[i, 2] if content_features.shape[1] > 2 else 150.0
        
        # Calculate K-factor
        k_factor = calculate_virality_coefficient_fast(
            engagement_rates[i],
            share_prob,
            network_reach,
            uniqueness
        )
        
        # Calculate viral score (0-100)
        viral_score = k_factor * 20.0  # Scale to 0-100 range
        if viral_score > 100.0:
            viral_score = 100.0
        
        # Simulate peak views (simplified)
        if k_factor > 1.0:
            peak_views = 1000.0 * pow(k_factor, 5.0)  # Exponential growth potential
        else:
            peak_views = 1000.0 * k_factor  # Linear for sub-viral
        
        # Apply platform multiplier
        if 0 <= platform_ids[i] < 5:
            peak_views *= PLATFORM_COEFFICIENTS[platform_ids[i]]
        
        # Store results
        results[i * 3] = viral_score
        results[i * 3 + 1] = k_factor
        results[i * 3 + 2] = peak_views


# Python wrapper functions for easy use
def fast_viral_analysis(content_params):
    """
    Python wrapper for fast viral analysis
    
    Args:
        content_params: Dictionary with content parameters
        
    Returns:
        Dictionary with viral metrics
    """
    # Extract parameters
    hashtags = np.asarray(content_params.get('hashtag_scores', [0.8, 0.7, 0.6]), dtype=np.float64)
    timing = np.asarray(content_params.get('timing_factors', [0.9, 0.8]), dtype=np.float64)
    emotional = content_params.get('emotional_intensity', 0.7)
    platform_id = content_params.get('platform_id', 0)
    
    # Calculate engagement
    engagement = calculate_engagement_score_fast(hashtags, timing, emotional, platform_id)
    
    # Calculate virality
    share_prob = content_params.get('share_probability', 0.15)
    network_reach = content_params.get('network_reach', 150.0)
    uniqueness = content_params.get('uniqueness', 0.8)
    
    k_factor = calculate_virality_coefficient_fast(
        engagement, share_prob, network_reach, uniqueness
    )
    
    # Simulate growth
    initial_views = content_params.get('initial_views', 100.0)
    decay_rate = content_params.get('decay_rate', 0.05)
    time_steps = content_params.get('time_steps', 168)  # 1 week hourly
    external_boosts = np.zeros(time_steps, dtype=np.float64)
    
    growth_curve = simulate_viral_growth_fast(
        initial_views, k_factor, decay_rate, time_steps, external_boosts
    )
    
    # Calculate peak and total
    peak_views = np.max(growth_curve)
    total_views = np.sum(growth_curve)
    
    return {
        'engagement_score': engagement,
        'virality_coefficient': k_factor,
        'is_viral': k_factor > 1.0,
        'peak_views': peak_views,
        'total_views': total_views,
        'viral_score': min(k_factor * 20.0, 100.0)
    }


def optimize_for_virality(content, platform='TIKTOK'):
    """
    Optimize content parameters for maximum virality
    
    Args:
        content: Content dictionary
        platform: Target platform
        
    Returns:
        Optimized parameters
    """
    platform_map = {
        'TIKTOK': 0,
        'INSTAGRAM': 1,
        'YOUTUBE': 2,
        'TWITTER': 3,
        'LINKEDIN': 4
    }
    
    platform_id = platform_map.get(platform, 0)
    
    # Start with current parameters
    params = {
        'hashtag_scores': content.get('hashtag_scores', [0.8, 0.7, 0.6]),
        'timing_factors': content.get('timing_factors', [0.9, 0.8]),
        'emotional_intensity': content.get('emotional_intensity', 0.7),
        'platform_id': platform_id,
        'share_probability': 0.15,
        'network_reach': 150.0,
        'uniqueness': content.get('uniqueness', 0.8)
    }
    
    # Optimize for platform
    if platform == 'TIKTOK':
        params['emotional_intensity'] = min(params['emotional_intensity'] * 1.2, 1.0)
        params['hashtag_scores'] = [min(s * 1.1, 1.0) for s in params['hashtag_scores']]
    elif platform == 'INSTAGRAM':
        params['uniqueness'] = min(params['uniqueness'] * 1.15, 1.0)
    elif platform == 'YOUTUBE':
        params['timing_factors'] = [min(t * 1.1, 1.0) for t in params['timing_factors']]
    
    # Calculate optimized metrics
    results = fast_viral_analysis(params)
    
    return {
        'optimized_params': params,
        'predicted_engagement': results['engagement_score'],
        'predicted_virality': results['virality_coefficient'],
        'predicted_peak_views': results['peak_views'],
        'optimization_factor': results['virality_coefficient'] / max(content.get('base_virality', 0.5), 0.1)
    }