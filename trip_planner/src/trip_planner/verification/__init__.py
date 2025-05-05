"""
Verification module for MAIA system.

This module provides constraint verification functionality 
for the hierarchical multi-agent travel planning system.
"""

from .constraint_manager import (
    ConstraintManager,
    ConstraintViolation,
    LayerVerificationResult,
    VerificationResult
)

__all__ = [
    'ConstraintManager',
    'ConstraintViolation',
    'LayerVerificationResult',
    'VerificationResult'
]