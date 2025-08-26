"""
Personality Matrix (PMX) - Core personality management system.

This module provides the main PersonalityMatrix class that orchestrates
all personality-related functionality including traits, states, style synthesis,
and boundary management.
"""

from .core import PersonalityMatrix
from .models import (
    StyleProfile,
    StateUpdate,
    TraitKernel,
    AffectiveState,
    StyleTrace,
    DecodingProfile,
    BoundaryCaps,
    AudienceContext,
    ChannelContext,
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
    "AudienceContext",
    "ChannelContext",
]