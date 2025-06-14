# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: nonecheck=False
# cython: cdivision=True
"""
Cython-optimized Fractal Calculations
=====================================

High-performance fractal dimension and pattern analysis.
"""

import numpy as np
cimport numpy as np
cimport cython
from libc.math cimport log, floor, sqrt, pow, fabs
from cython.parallel import prange
import cython.parallel

# Type definitions
ctypedef np.float64_t DOUBLE
ctypedef np.int32_t INT32

# Constants
cdef double PHI = 1.618033988749895
cdef double LOG_PHI = 0.48121182505960347


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_box_dimension_fast(double[:] data, double[:] scales):
    """
    Fast box-counting fractal dimension
    
    Args:
        data: 1D data array
        scales: Array of scales to test
        
    Returns:
        Fractal dimension
    """
    cdef int i, j
    cdef int n_data = data.shape[0]
    cdef int n_scales = scales.shape[0]
    cdef double scale
    cdef int count
    cdef int curr_box, prev_box
    
    # Arrays for log-log regression
    cdef double[:] log_scales = np.zeros(n_scales, dtype=np.float64)
    cdef double[:] log_counts = np.zeros(n_scales, dtype=np.float64)
    
    # Calculate box counts for each scale
    for i in range(n_scales):
        scale = scales[i]
        count = 1  # At least one box
        
        prev_box = <int>floor(data[0] / scale)
        
        for j in range(1, n_data):
            curr_box = <int>floor(data[j] / scale)
            if curr_box != prev_box:
                count += 1
                prev_box = curr_box
        
        log_scales[i] = log(scale)
        log_counts[i] = log(<double>count)
    
    # Linear regression in log-log space
    cdef double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0
    
    for i in range(n_scales):
        sum_x += log_scales[i]
        sum_y += log_counts[i]
        sum_xx += log_scales[i] * log_scales[i]
        sum_xy += log_scales[i] * log_counts[i]
    
    cdef double slope = (n_scales * sum_xy - sum_x * sum_y) / (n_scales * sum_xx - sum_x * sum_x)
    cdef double dimension = -slope
    
    # Clip to reasonable range
    if dimension < 0.0:
        dimension = 0.0
    elif dimension > 3.0:
        dimension = 3.0
    
    return dimension


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef double calculate_lacunarity_fast(double[:] data, int[:] box_sizes):
    """
    Fast lacunarity calculation
    
    Args:
        data: 1D data array
        box_sizes: Array of box sizes
        
    Returns:
        Lacunarity value
    """
    cdef int i, j, k
    cdef int n_data = data.shape[0]
    cdef int n_boxes = box_sizes.shape[0]
    cdef double mean_data = 0.0
    cdef double lacunarity_sum = 0.0
    cdef int box_size, n_samples
    cdef double box_sum, box_mean, box_var
    cdef double mean_mass, var_mass
    
    # Calculate mean of data
    for i in range(n_data):
        mean_data += data[i]
    mean_data /= n_data
    
    # Calculate lacunarity for each box size
    for i in range(n_boxes):
        box_size = box_sizes[i]
        if box_size > n_data:
            continue
        
        n_samples = n_data - box_size + 1
        mean_mass = 0.0
        var_mass = 0.0
        
        # Calculate box masses
        for j in range(n_samples):
            box_sum = 0.0
            
            # Sum values in box
            for k in range(box_size):
                if data[j + k] > mean_data:
                    box_sum += 1.0
            
            mean_mass += box_sum
        
        mean_mass /= n_samples
        
        # Calculate variance
        for j in range(n_samples):
            box_sum = 0.0
            
            for k in range(box_size):
                if data[j + k] > mean_data:
                    box_sum += 1.0
            
            var_mass += pow(box_sum - mean_mass, 2)
        
        var_mass /= n_samples
        
        # Lacunarity for this box size
        if mean_mass > 0:
            lacunarity_sum += 1.0 + var_mass / (mean_mass * mean_mass)
    
    if n_boxes > 0:
        return lacunarity_sum / n_boxes
    else:
        return 1.0


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
@cython.nogil
cdef double hurst_rs_analysis(double[:] data, int lag) nogil:
    """
    R/S analysis for a single lag (nogil for parallelization)
    """
    cdef int i, j
    cdef int n = data.shape[0]
    cdef int n_chunks = (n - lag + 1) // lag
    cdef double rs_sum = 0.0
    cdef double chunk_mean, y_sum, R, S
    cdef double y_min, y_max
    
    for i in range(n_chunks):
        # Calculate mean of chunk
        chunk_mean = 0.0
        for j in range(lag):
            chunk_mean += data[i * lag + j]
        chunk_mean /= lag
        
        # Calculate cumulative deviation
        y_sum = 0.0
        y_min = 0.0
        y_max = 0.0
        
        for j in range(lag):
            y_sum += data[i * lag + j] - chunk_mean
            if y_sum < y_min:
                y_min = y_sum
            if y_sum > y_max:
                y_max = y_sum
        
        # Range
        R = y_max - y_min
        
        # Standard deviation
        S = 0.0
        for j in range(lag):
            S += pow(data[i * lag + j] - chunk_mean, 2)
        S = sqrt(S / lag)
        
        # R/S ratio
        if S > 0:
            rs_sum += R / S
    
    if n_chunks > 0:
        return rs_sum / n_chunks
    else:
        return 0.0


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double calculate_hurst_exponent_fast(double[:] data):
    """
    Fast Hurst exponent calculation using R/S analysis
    
    Args:
        data: Time series data
        
    Returns:
        Hurst exponent
    """
    cdef int i
    cdef int n = data.shape[0]
    cdef int n_lags = min(20, n // 2)
    
    # Arrays for regression
    cdef double[:] log_lags = np.zeros(n_lags - 1, dtype=np.float64)
    cdef double[:] log_rs = np.zeros(n_lags - 1, dtype=np.float64)
    
    # Calculate R/S for each lag (parallel)
    for i in prange(2, n_lags + 1, nogil=True):
        log_lags[i - 2] = log(<double>i)
        log_rs[i - 2] = log(hurst_rs_analysis(data, i))
    
    # Linear regression
    cdef double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0
    cdef int valid_points = 0
    
    for i in range(n_lags - 1):
        if log_rs[i] == log_rs[i]:  # Check for NaN
            sum_x += log_lags[i]
            sum_y += log_rs[i]
            sum_xx += log_lags[i] * log_lags[i]
            sum_xy += log_lags[i] * log_rs[i]
            valid_points += 1
    
    if valid_points < 2:
        return 0.5  # Default
    
    cdef double hurst = (valid_points * sum_xy - sum_x * sum_y) / (valid_points * sum_xx - sum_x * sum_x)
    
    # Clip to [0, 1]
    if hurst < 0.0:
        hurst = 0.0
    elif hurst > 1.0:
        hurst = 1.0
    
    return hurst


@cython.boundscheck(False)
@cython.wraparound(False)
cpdef double calculate_phi_fractal_alignment(double[:] data):
    """
    Calculate alignment with φ-based fractal patterns
    
    Args:
        data: Input data
        
    Returns:
        φ alignment score (0-1)
    """
    cdef int i
    cdef int n = data.shape[0]
    cdef double alignment = 0.0
    cdef double phi_ratio
    cdef int phi_points[5]
    
    # Calculate φ-based positions
    phi_points[0] = <int>(n / PHI / PHI)
    phi_points[1] = <int>(n / PHI)
    phi_points[2] = n // 2
    phi_points[3] = <int>(n * INV_PHI)
    phi_points[4] = <int>(n * INV_PHI * INV_PHI)
    
    # Check data values at φ points
    cdef double sum_phi_values = 0.0
    cdef double sum_all_values = 0.0
    
    for i in range(n):
        sum_all_values += fabs(data[i])
    
    for i in range(5):
        if 0 <= phi_points[i] < n:
            sum_phi_values += fabs(data[phi_points[i]])
    
    if sum_all_values > 0:
        phi_ratio = sum_phi_values / sum_all_values * 5.0
        
        # Calculate alignment based on how close ratio is to φ
        alignment = 1.0 - fabs(phi_ratio - PHI) / PHI
        
        if alignment < 0.0:
            alignment = 0.0
        elif alignment > 1.0:
            alignment = 1.0
    
    return alignment


# Python wrapper for batch fractal analysis
def fast_fractal_analysis(data_array):
    """
    Fast fractal analysis of data
    
    Args:
        data_array: NumPy array of data
        
    Returns:
        Dictionary with fractal metrics
    """
    data = np.asarray(data_array, dtype=np.float64)
    
    # Scales for box dimension
    scales = np.logspace(-2, 0, 15, dtype=np.float64)
    
    # Box sizes for lacunarity
    box_sizes = np.array([2, 4, 8, 16, 32], dtype=np.int32)
    
    # Calculate metrics
    dimension = calculate_box_dimension_fast(data, scales)
    lacunarity = calculate_lacunarity_fast(data, box_sizes)
    hurst = calculate_hurst_exponent_fast(data)
    phi_alignment = calculate_phi_fractal_alignment(data)
    
    return {
        'fractal_dimension': dimension,
        'lacunarity': lacunarity,
        'hurst_exponent': hurst,
        'phi_alignment': phi_alignment,
        'self_similarity': 1.0 - abs(hurst - 0.5) * 2  # Peak at H=0.5
    }