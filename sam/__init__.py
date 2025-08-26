"""
Sam's Autonomous AI System - Personality Matrix Component

This package contains the Personality Matrix (PMX) component that provides
persistent personality management for autonomous AI systems.
"""

__version__ = "1.0.0"
__author__ = "Sam AI"
__email__ = "sam@aegis.ai"

from .persona import PersonalityMatrix
from .persona.models import (
    StyleProfile,
    StateUpdate,
    TraitKernel,
    AffectiveState,
    StyleTrace,
    DecodingProfile,
    BoundaryCaps,
)

__all__ = [
    "PersonalityMatrix",
    "StyleProfile",
    "StateUpdate",
    "TraitKernel",
    "AffectiveState",
    "StyleTrace",
    "DecodingProfile",
    "BoundaryCaps",
]