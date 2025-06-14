#!/usr/bin/env python3
"""
Cython Setup for ProStudio Performance Extensions
================================================

Compile with: python setup.py build_ext --inplace
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np

# Define Cython extensions
extensions = [
    Extension(
        "consciousness_metrics_cy",
        ["consciousness_metrics.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3", "-march=native", "-ffast-math"],
        language="c++"
    ),
    Extension(
        "fractal_calculations_cy",
        ["fractal_calculations.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3", "-march=native", "-ffast-math", "-fopenmp"],
        extra_link_args=["-fopenmp"],
        language="c++"
    ),
    Extension(
        "viral_scoring_cy",
        ["viral_scoring.pyx"],
        include_dirs=[np.get_include()],
        extra_compile_args=["-O3", "-march=native", "-ffast-math"],
        language="c++"
    )
]

setup(
    name="ProStudio Acceleration",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'nonecheck': False,
            'cdivision': True,
            'profile': False
        }
    ),
    zip_safe=False
)