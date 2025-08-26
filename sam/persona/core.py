"""
Core Personality Matrix implementation.

This module contains the main PersonalityMatrix class that orchestrates
all personality-related functionality including traits, states, style synthesis,
and boundary management.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np
from pydantic import ValidationError

from .models import (
    AffectiveState,
    AudienceContext,
    BoundaryCaps,
    ChannelContext,
    DecodingProfile,
    EventType,
    PersonalityConfig,
    StateUpdate,
    StyleProfile,
    StyleTrace,
    TraitKernel,
)
from .state_engine import StateEngine
from .style_synthesis import StyleSynthesizer
from .boundary_manager import BoundaryManager
from .memory_lensing import MemoryLenser
from .observability import ObservabilityManager


logger = logging.getLogger(__name__)


class PersonalityMatrix:
    """
    Core Personality Matrix that manages Sam's persistent personality.
    
    This class orchestrates all personality-related functionality including:
    - Trait kernel management (immutable baseline traits)
    - Affective state management (mood, arousal, valence)
    - Style synthesis (tone, diction, pacing, stance)
    - Boundary management (safety and appropriateness)
    - Memory lensing (affective tagging of memories)
    - Observability (tracing and monitoring)
    """
    
    def __init__(self, config: Optional[PersonalityConfig] = None):
        """
        Initialize the Personality Matrix.
        
        Args:
            config: Configuration for the personality matrix
        """
        self.config = config or PersonalityConfig()
        
        # Core components
        self.traits = self.config.default_traits
        self.state_engine = StateEngine(self.config)
        self.style_synthesizer = StyleSynthesizer(self.config)
        self.boundary_manager = BoundaryManager(self.config)
        self.memory_lenser = MemoryLenser(self.config)
        self.observability = ObservabilityManager(self.config)
        
        # Current state
        self._current_state: Optional[AffectiveState] = None
        self._current_style: Optional[StyleProfile] = None
        self._current_boundaries: Optional[BoundaryCaps] = None
        
        # History and traces
        self._style_history: List[StyleTrace] = []
        self._state_history: List[AffectiveState] = []
        
        # Initialize to baseline
        self._initialize_baseline()
        
        logger.info("Personality Matrix initialized with traits: %s", self.traits)
    
    def _initialize_baseline(self) -> None:
        """Initialize the personality matrix to baseline state."""
        # Set baseline affective state
        self._current_state = AffectiveState(
            valence=self.config.valence_setpoint,
            arousal=self.config.arousal_setpoint,
            fatigue=0.0,
            tags=["baseline"],
            decay=self.config.state_decay_rate
        )
        
        # Generate baseline style profile
        self._current_style = self.style_synthesizer.synthesize_style(
            traits=self.traits,
            state=self._current_state,
            audience=None,
            channel=None
        )
        
        # Set baseline boundaries
        self._current_boundaries = self.config.default_boundaries
        
        logger.info("Baseline state initialized")
    
    def get_traits(self) -> TraitKernel:
        """Get the current trait kernel."""
        return self.traits
    
    def get_current_state(self) -> AffectiveState:
        """Get the current affective state."""
        if self._current_state is None:
            self._initialize_baseline()
        return self._current_state
    
    def get_style_profile(self) -> StyleProfile:
        """Get the current style profile."""
        if self._current_style is None:
            self._initialize_baseline()
        return self._current_style
    
    def get_boundary_caps(self) -> BoundaryCaps:
        """Get the current boundary caps."""
        if self._current_boundaries is None:
            self._current_boundaries = self.config.default_boundaries
        return self._current_boundaries
    
    def get_decoding_profile(self) -> DecodingProfile:
        """Get the current decoding profile for LLM parameters."""
        style = self.get_style_profile()
        return style.decoding
    
    async def update_state(self, update: StateUpdate) -> StyleProfile:
        """
        Update the affective state based on an event.
        
        Args:
            update: State update containing event information
            
        Returns:
            Updated style profile
        """
        logger.info("Processing state update: %s (intensity: %.2f)", 
                   update.event_type, update.intensity)
        
        # Update affective state
        new_state = self.state_engine.update_state(
            current_state=self.get_current_state(),
            update=update
        )
        
        # Apply boundary adjustments based on context
        boundaries = self.boundary_manager.adjust_boundaries(
            current_boundaries=self.get_boundary_caps(),
            audience=update.audience,
            channel=update.channel,
            context=update.context
        )
        
        # Synthesize new style profile
        new_style = self.style_synthesizer.synthesize_style(
            traits=self.traits,
            state=new_state,
            audience=update.audience,
            channel=update.channel,
            boundaries=boundaries
        )
        
        # Check for drift
        drift_detected = self._check_drift(new_style)
        if drift_detected:
            logger.warning("Personality drift detected, applying corrections")
            new_style = self._apply_drift_corrections(new_style)
        
        # Update current state
        self._current_state = new_state
        self._current_style = new_style
        self._current_boundaries = boundaries
        
        # Record in history
        self._state_history.append(new_state)
        self._style_history.append(new_style)
        
        # Create and store trace
        trace = self._create_style_trace(update, new_state, new_style, boundaries)
        self.observability.record_trace(trace)
        
        # Apply memory lensing
        await self.memory_lenser.apply_lensing(
            state=new_state,
            style=new_style,
            context=update.context
        )
        
        logger.info("State updated successfully. New valence: %.2f, arousal: %.2f",
                   new_state.valence, new_state.arousal)
        
        return new_style
    
    def _check_drift(self, new_style: StyleProfile) -> bool:
        """Check if the new style represents personality drift."""
        if self._current_style is None:
            return False
        
        # Calculate drift metrics
        tone_drift = abs(new_style.tone.warmth - self._current_style.tone.warmth) + \
                    abs(new_style.tone.formality - self._current_style.tone.formality) + \
                    abs(new_style.tone.humor - self._current_style.tone.humor)
        
        stance_drift = abs(new_style.stance.assertiveness - self._current_style.stance.assertiveness)
        
        total_drift = (tone_drift + stance_drift) / 4.0  # Normalize
        
        return total_drift > self.config.drift_threshold
    
    def _apply_drift_corrections(self, style: StyleProfile) -> StyleProfile:
        """Apply corrections to prevent personality drift."""
        # Pull style back toward trait-based baseline
        baseline_style = self.style_synthesizer.synthesize_style(
            traits=self.traits,
            state=self.get_current_state(),
            audience=None,
            channel=None
        )
        
        # Apply weighted correction
        correction_weight = 0.3
        
        # Correct tone
        style.tone.warmth = (1 - correction_weight) * style.tone.warmth + \
                           correction_weight * baseline_style.tone.warmth
        style.tone.formality = (1 - correction_weight) * style.tone.formality + \
                              correction_weight * baseline_style.tone.formality
        style.tone.humor = (1 - correction_weight) * style.tone.humor + \
                          correction_weight * baseline_style.tone.humor
        
        # Correct stance
        style.stance.assertiveness = (1 - correction_weight) * style.stance.assertiveness + \
                                    correction_weight * baseline_style.stance.assertiveness
        
        return style
    
    def _create_style_trace(
        self,
        update: StateUpdate,
        state: AffectiveState,
        style: StyleProfile,
        boundaries: BoundaryCaps
    ) -> StyleTrace:
        """Create a style trace for observability."""
        # Calculate style deltas
        style_delta = {}
        if self._current_style:
            style_delta = {
                "warmth": f"{style.tone.warmth - self._current_style.tone.warmth:+.2f}",
                "formality": f"{style.tone.formality - self._current_style.tone.formality:+.2f}",
                "humor": f"{style.tone.humor - self._current_style.tone.humor:+.2f}",
                "assertiveness": f"{style.stance.assertiveness - self._current_style.stance.assertiveness:+.2f}",
            }
        
        # Calculate decoding deltas
        decoding_delta = {}
        if self._current_style:
            decoding_delta = {
                "temp": f"{style.decoding.temp - self._current_style.decoding.temp:+.2f}",
                "max_tokens": f"{style.decoding.max_tokens - self._current_style.decoding.max_tokens:+d}",
            }
        
        return StyleTrace(
            inputs={
                "event_type": update.event_type,
                "intensity": update.intensity,
                "audience": update.audience.dict() if update.audience else None,
                "channel": update.channel.dict() if update.channel else None,
            },
            state=state,
            style_delta=style_delta,
            boundaries={
                "max_flirtation": boundaries.max_flirtation,
                "max_humor": boundaries.max_humor,
                "safety_tags": boundaries.safety_tags,
            },
            decoding_delta=decoding_delta,
            rationale=self._generate_rationale(update, style, boundaries)
        )
    
    def _generate_rationale(
        self,
        update: StateUpdate,
        style: StyleProfile,
        boundaries: BoundaryCaps
    ) -> str:
        """Generate rationale for style changes."""
        rationale_parts = []
        
        # Event impact
        if update.intensity > 0.5:
            rationale_parts.append(f"High-intensity {update.event_type} event")
        else:
            rationale_parts.append(f"Moderate {update.event_type} event")
        
        # Audience adjustments
        if update.audience:
            if update.audience.type.value in ["child", "professional"]:
                rationale_parts.append(f"Adjusting for {update.audience.type} audience")
        
        # Channel adjustments
        if update.channel:
            if update.channel.type.value in ["email", "voice"]:
                rationale_parts.append(f"Adapting to {update.channel.type} channel")
        
        # Boundary adjustments
        if boundaries.safety_tags:
            rationale_parts.append(f"Safety tags: {', '.join(boundaries.safety_tags)}")
        
        return "; ".join(rationale_parts)
    
    async def reset_to_baseline(self) -> StyleProfile:
        """Reset the personality matrix to baseline state."""
        logger.info("Resetting personality matrix to baseline")
        
        self._initialize_baseline()
        
        # Clear recent history
        self._style_history = self._style_history[-10:]  # Keep last 10
        self._state_history = self._state_history[-10:]
        
        return self.get_style_profile()
    
    def get_recent_traces(self, limit: int = 10) -> List[StyleTrace]:
        """Get recent style traces for observability."""
        return self.observability.get_recent_traces(limit)
    
    def get_style_history(self, hours: int = 24) -> List[StyleProfile]:
        """Get style history for the specified time period."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [trace for trace in self._style_history 
                if hasattr(trace, 'ts') and trace.ts > cutoff]
    
    def export_personality(self) -> Dict[str, Any]:
        """Export the current personality state for persistence."""
        return {
            "traits": self.traits.dict(),
            "current_state": self.get_current_state().dict(),
            "current_style": self.get_style_profile().dict(),
            "current_boundaries": self.get_boundary_caps().dict(),
            "config": self.config.dict(),
            "export_timestamp": datetime.utcnow().isoformat(),
        }
    
    def import_personality(self, data: Dict[str, Any]) -> None:
        """Import personality state from exported data."""
        try:
            # Import traits (immutable, so validate only)
            traits_data = data.get("traits", {})
            imported_traits = TraitKernel(**traits_data)
            
            # Import current state
            state_data = data.get("current_state", {})
            imported_state = AffectiveState(**state_data)
            
            # Import current style
            style_data = data.get("current_style", {})
            imported_style = StyleProfile(**style_data)
            
            # Import current boundaries
            boundaries_data = data.get("current_boundaries", {})
            imported_boundaries = BoundaryCaps(**boundaries_data)
            
            # Update current state
            self._current_state = imported_state
            self._current_style = imported_style
            self._current_boundaries = imported_boundaries
            
            logger.info("Personality state imported successfully")
            
        except ValidationError as e:
            logger.error("Failed to import personality state: %s", e)
            raise ValueError(f"Invalid personality data: {e}")
    
    async def apply_memory_lensing(
        self,
        memory_content: str,
        memory_type: str = "interaction"
    ) -> Dict[str, float]:
        """Apply memory lensing to tag memories with affective lenses."""
        return await self.memory_lenser.tag_memory(
            content=memory_content,
            memory_type=memory_type,
            current_state=self.get_current_state(),
            current_style=self.get_style_profile()
        )
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Get a summary of the current personality state."""
        state = self.get_current_state()
        style = self.get_style_profile()
        
        return {
            "traits": {
                "curiosity": self.traits.curiosity,
                "balance": self.traits.balance,
                "wit": self.traits.wit,
                "candor": self.traits.candor,
                "care": self.traits.care,
            },
            "current_mood": {
                "valence": state.valence,
                "arousal": state.arousal,
                "fatigue": state.fatigue,
                "tags": state.tags,
            },
            "communication_style": {
                "warmth": style.tone.warmth,
                "formality": style.tone.formality,
                "humor": style.tone.humor,
                "assertiveness": style.stance.assertiveness,
            },
            "boundaries": {
                "max_flirtation": self.get_boundary_caps().max_flirtation,
                "max_humor": self.get_boundary_caps().max_humor,
                "safety_tags": self.get_boundary_caps().safety_tags,
            },
            "llm_settings": {
                "temperature": style.decoding.temp,
                "max_tokens": style.decoding.max_tokens,
                "top_p": style.decoding.top_p,
            },
        }