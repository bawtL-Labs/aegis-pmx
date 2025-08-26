"""
Style Synthesis for personality-driven communication.

This module handles the synthesis of communication style profiles by blending
traits, states, audience context, and channel information.
"""

import logging
from typing import Dict, Optional

import numpy as np

from .models import (
    AffectiveState,
    AudienceContext,
    BoundaryCaps,
    ChannelContext,
    DecodingProfile,
    PersonalityConfig,
    SentenceLength,
    StyleProfile,
    ToneProfile,
    DictionProfile,
    PacingProfile,
    StanceProfile,
    BoundaryProfile,
    TraitKernel,
)


logger = logging.getLogger(__name__)


class StyleSynthesizer:
    """
    Synthesizes communication style profiles from personality components.
    
    This class implements the style mapping algorithm:
    Linear blend of traits, state, mode, audience; clamp via boundary bands.
    """
    
    def __init__(self, config: PersonalityConfig):
        """
        Initialize the style synthesizer.
        
        Args:
            config: Personality configuration
        """
        self.config = config
        
        # Style mapping weights
        self._weights = self._initialize_weights()
        
        # Audience and channel modifiers
        self._audience_modifiers = self._initialize_audience_modifiers()
        self._channel_modifiers = self._initialize_channel_modifiers()
        
        # Decoding parameter mappings
        self._decoding_mappings = self._initialize_decoding_mappings()
        
        logger.info("Style Synthesizer initialized")
    
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize weights for different style components."""
        return {
            "traits": 0.4,      # Base personality traits
            "state": 0.3,       # Current affective state
            "audience": 0.2,    # Audience context
            "channel": 0.1,     # Communication channel
        }
    
    def _initialize_audience_modifiers(self) -> Dict[str, Dict[str, float]]:
        """Initialize audience-based style modifiers."""
        return {
            "friend": {
                "warmth": 1.3,
                "formality": 0.6,
                "humor": 1.2,
                "flirtation": 1.1,
                "assertiveness": 1.1,
            },
            "family": {
                "warmth": 1.4,
                "formality": 0.5,
                "humor": 1.1,
                "flirtation": 0.8,
                "assertiveness": 1.0,
            },
            "colleague": {
                "warmth": 0.9,
                "formality": 1.2,
                "humor": 0.8,
                "flirtation": 0.3,
                "assertiveness": 1.1,
            },
            "stranger": {
                "warmth": 0.8,
                "formality": 1.1,
                "humor": 0.7,
                "flirtation": 0.2,
                "assertiveness": 0.9,
            },
            "child": {
                "warmth": 1.5,
                "formality": 0.3,
                "humor": 1.3,
                "flirtation": 0.1,
                "assertiveness": 0.8,
            },
            "professional": {
                "warmth": 0.7,
                "formality": 1.4,
                "humor": 0.6,
                "flirtation": 0.1,
                "assertiveness": 1.2,
            },
            "intimate": {
                "warmth": 1.6,
                "formality": 0.2,
                "humor": 1.0,
                "flirtation": 1.4,
                "assertiveness": 1.0,
            },
        }
    
    def _initialize_channel_modifiers(self) -> Dict[str, Dict[str, float]]:
        """Initialize channel-based style modifiers."""
        return {
            "chat": {
                "warmth": 1.0,
                "formality": 0.8,
                "humor": 1.1,
                "expansiveness": 0.9,
                "sentence_len": "medium",
            },
            "email": {
                "warmth": 0.9,
                "formality": 1.2,
                "humor": 0.8,
                "expansiveness": 1.1,
                "sentence_len": "long",
            },
            "voice": {
                "warmth": 1.2,
                "formality": 0.7,
                "humor": 1.2,
                "expansiveness": 1.0,
                "sentence_len": "medium",
            },
            "video": {
                "warmth": 1.1,
                "formality": 0.9,
                "humor": 1.0,
                "expansiveness": 0.8,
                "sentence_len": "short",
            },
            "text": {
                "warmth": 0.8,
                "formality": 1.0,
                "humor": 0.9,
                "expansiveness": 0.7,
                "sentence_len": "short",
            },
        }
    
    def _initialize_decoding_mappings(self) -> Dict[str, Dict[str, float]]:
        """Initialize mappings from style to LLM decoding parameters."""
        return {
            "warmth_to_temp": 0.3,      # Higher warmth = higher temperature
            "humor_to_temp": 0.4,       # Higher humor = higher temperature
            "formality_to_penalty": -0.2,  # Higher formality = lower penalty
            "expansiveness_to_tokens": 0.5,  # Higher expansiveness = more tokens
            "assertiveness_to_top_p": 0.1,   # Higher assertiveness = higher top_p
        }
    
    def synthesize_style(
        self,
        traits: TraitKernel,
        state: AffectiveState,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None,
        boundaries: Optional[BoundaryCaps] = None
    ) -> StyleProfile:
        """
        Synthesize a complete style profile from personality components.
        
        Args:
            traits: Personality traits
            state: Current affective state
            audience: Audience context
            channel: Channel context
            boundaries: Boundary constraints
            
        Returns:
            Synthesized style profile
        """
        logger.debug("Synthesizing style profile")
        
        # Generate base tone from traits and state
        base_tone = self._synthesize_tone(traits, state, audience, channel)
        
        # Generate diction profile
        diction = self._synthesize_diction(traits, state, audience, channel)
        
        # Generate pacing profile
        pacing = self._synthesize_pacing(traits, state, audience, channel)
        
        # Generate stance profile
        stance = self._synthesize_stance(traits, state, audience, channel)
        
        # Generate boundary profile
        boundary_profile = self._synthesize_boundaries(boundaries, audience, channel)
        
        # Generate decoding profile
        decoding = self._synthesize_decoding(base_tone, pacing, stance)
        
        # Create complete style profile
        style = StyleProfile(
            tone=base_tone,
            diction=diction,
            pacing=pacing,
            stance=stance,
            boundaries=boundary_profile,
            decoding=decoding,
        )
        
        # Apply boundary constraints
        style = self._apply_boundary_constraints(style, boundaries)
        
        logger.debug("Style synthesis complete: warmth=%.2f, formality=%.2f, humor=%.2f",
                    style.tone.warmth, style.tone.formality, style.tone.humor)
        
        return style
    
    def _synthesize_tone(
        self,
        traits: TraitKernel,
        state: AffectiveState,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None
    ) -> ToneProfile:
        """Synthesize tone characteristics."""
        # Base tone from traits
        base_warmth = traits.care * 0.8 + traits.balance * 0.2
        base_formality = 1.0 - traits.candor * 0.6 - traits.wit * 0.4
        base_humor = traits.wit * 0.8 + traits.curiosity * 0.2
        base_flirtation = traits.candor * 0.4 + traits.wit * 0.3
        
        # State influence
        state_warmth = (state.valence + 1.0) / 2.0  # Map valence to warmth
        state_formality = 1.0 - state.arousal * 0.3  # Higher arousal = less formal
        state_humor = (state.valence + 1.0) / 2.0 * (1.0 - state.fatigue * 0.5)
        state_flirtation = (state.valence + 1.0) / 2.0 * (1.0 - state.fatigue * 0.3)
        
        # Blend components
        weights = self._weights
        warmth = (base_warmth * weights["traits"] + 
                 state_warmth * weights["state"])
        formality = (base_formality * weights["traits"] + 
                    state_formality * weights["state"])
        humor = (base_humor * weights["traits"] + 
                state_humor * weights["state"])
        flirtation = (base_flirtation * weights["traits"] + 
                     state_flirtation * weights["state"])
        
        # Apply audience modifiers
        if audience:
            audience_mod = self._audience_modifiers.get(audience.type.value, {})
            warmth *= audience_mod.get("warmth", 1.0)
            formality *= audience_mod.get("formality", 1.0)
            humor *= audience_mod.get("humor", 1.0)
            flirtation *= audience_mod.get("flirtation", 1.0)
        
        # Apply channel modifiers
        if channel:
            channel_mod = self._channel_modifiers.get(channel.type.value, {})
            warmth *= channel_mod.get("warmth", 1.0)
            formality *= channel_mod.get("formality", 1.0)
            humor *= channel_mod.get("humor", 1.0)
        
        # Clamp values
        warmth = np.clip(warmth, 0.0, 1.0)
        formality = np.clip(formality, 0.0, 1.0)
        humor = np.clip(humor, 0.0, 1.0)
        flirtation = np.clip(flirtation, 0.0, 1.0)
        
        return ToneProfile(
            warmth=warmth,
            formality=formality,
            humor=humor,
            flirtation=flirtation,
        )
    
    def _synthesize_diction(
        self,
        traits: TraitKernel,
        state: AffectiveState,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None
    ) -> DictionProfile:
        """Synthesize diction characteristics."""
        # Base sentence length from traits and state
        if traits.curiosity > 0.7 and state.arousal > 0.5:
            sentence_len = SentenceLength.LONG
        elif traits.candor > 0.8 or state.fatigue > 0.6:
            sentence_len = SentenceLength.SHORT
        else:
            sentence_len = SentenceLength.MEDIUM
        
        # Channel override
        if channel:
            channel_mod = self._channel_modifiers.get(channel.type.value, {})
            if "sentence_len" in channel_mod:
                sentence_len = SentenceLength(channel_mod["sentence_len"])
        
        # Metaphor density from traits
        metaphor_density = traits.wit * 0.6 + traits.curiosity * 0.4
        
        # State influence
        metaphor_density *= (1.0 - state.fatigue * 0.3)  # Less metaphors when tired
        
        # Audience influence
        if audience and audience.type.value == "child":
            metaphor_density *= 1.2  # More metaphors for children
        elif audience and audience.type.value == "professional":
            metaphor_density *= 0.7  # Fewer metaphors in professional context
        
        metaphor_density = np.clip(metaphor_density, 0.0, 1.0)
        
        return DictionProfile(
            sentence_len=sentence_len,
            metaphor=metaphor_density,
        )
    
    def _synthesize_pacing(
        self,
        traits: TraitKernel,
        state: AffectiveState,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None
    ) -> PacingProfile:
        """Synthesize pacing characteristics."""
        # Base expansiveness from traits
        base_expansiveness = traits.curiosity * 0.7 + traits.candor * 0.3
        
        # State influence
        state_expansiveness = (state.arousal * 0.6 + (1.0 - state.fatigue) * 0.4)
        
        # Blend
        expansiveness = (base_expansiveness * self._weights["traits"] + 
                        state_expansiveness * self._weights["state"])
        
        # Channel influence
        if channel:
            channel_mod = self._channel_modifiers.get(channel.type.value, {})
            expansiveness *= channel_mod.get("expansiveness", 1.0)
        
        expansiveness = np.clip(expansiveness, 0.0, 1.0)
        
        return PacingProfile(expansiveness=expansiveness)
    
    def _synthesize_stance(
        self,
        traits: TraitKernel,
        state: AffectiveState,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None
    ) -> StanceProfile:
        """Synthesize stance characteristics."""
        # Base assertiveness from traits
        base_assertiveness = traits.candor * 0.8 + traits.balance * 0.2
        
        # State influence
        state_assertiveness = (state.arousal * 0.5 + (state.valence + 1.0) / 2.0 * 0.5)
        
        # Blend
        assertiveness = (base_assertiveness * self._weights["traits"] + 
                        state_assertiveness * self._weights["state"])
        
        # Audience influence
        if audience:
            audience_mod = self._audience_modifiers.get(audience.type.value, {})
            assertiveness *= audience_mod.get("assertiveness", 1.0)
        
        assertiveness = np.clip(assertiveness, 0.0, 1.0)
        
        return StanceProfile(assertiveness=assertiveness)
    
    def _synthesize_boundaries(
        self,
        boundaries: Optional[BoundaryCaps] = None,
        audience: Optional[AudienceContext] = None,
        channel: Optional[ChannelContext] = None
    ) -> BoundaryProfile:
        """Synthesize boundary profile."""
        # Use provided boundaries or defaults
        if boundaries:
            max_flirtation = boundaries.max_flirtation
            max_humor = boundaries.max_humor
            max_candor = boundaries.max_candor
            min_formality = boundaries.min_formality
        else:
            max_flirtation = 0.5
            max_humor = 0.8
            max_candor = 0.9
            min_formality = 0.2
        
        # Determine sensitivity level
        sensitivity = "normal"
        if audience:
            if audience.type.value == "child":
                sensitivity = "soften"
            elif audience.type.value == "professional":
                sensitivity = "normal"
            elif audience.type.value == "intimate":
                sensitivity = "normal"
        
        # NSFW setting
        nsfw = False
        if audience and audience.type.value == "intimate":
            nsfw = True
        
        return BoundaryProfile(
            nsfw=nsfw,
            sensitive=sensitivity,
        )
    
    def _synthesize_decoding(
        self,
        tone: ToneProfile,
        pacing: PacingProfile,
        stance: StanceProfile
    ) -> DecodingProfile:
        """Synthesize LLM decoding parameters from style."""
        # Base parameters
        temp = 0.7
        top_p = 0.9
        top_k = 50
        penalty = 1.1
        max_tokens = 800
        
        # Apply style mappings
        mappings = self._decoding_mappings
        
        # Temperature adjustments
        temp += tone.warmth * mappings["warmth_to_temp"]
        temp += tone.humor * mappings["humor_to_temp"]
        
        # Penalty adjustments
        penalty += tone.formality * mappings["formality_to_penalty"]
        
        # Token adjustments
        max_tokens += int(pacing.expansiveness * mappings["expansiveness_to_tokens"] * 1000)
        
        # Top-p adjustments
        top_p += stance.assertiveness * mappings["assertiveness_to_top_p"]
        
        # Clamp to safe ranges
        temp = np.clip(temp, 0.1, 2.0)
        top_p = np.clip(top_p, 0.1, 1.0)
        top_k = np.clip(top_k, 1, 100)
        penalty = np.clip(penalty, 0.1, 2.0)
        max_tokens = np.clip(max_tokens, 100, 4000)
        
        return DecodingProfile(
            temp=temp,
            top_p=top_p,
            top_k=top_k,
            penalty=penalty,
            max_tokens=max_tokens,
        )
    
    def _apply_boundary_constraints(
        self,
        style: StyleProfile,
        boundaries: Optional[BoundaryCaps] = None
    ) -> StyleProfile:
        """Apply boundary constraints to the style profile."""
        if not boundaries:
            return style
        
        # Apply flirtation cap
        if style.tone.flirtation > boundaries.max_flirtation:
            style.tone.flirtation = boundaries.max_flirtation
        
        # Apply humor cap
        if style.tone.humor > boundaries.max_humor:
            style.tone.humor = boundaries.max_humor
        
        # Apply formality minimum
        if style.tone.formality < boundaries.min_formality:
            style.tone.formality = boundaries.min_formality
        
        return style
    
    def get_style_compatibility_score(
        self,
        style1: StyleProfile,
        style2: StyleProfile
    ) -> float:
        """
        Calculate compatibility score between two style profiles.
        
        Args:
            style1: First style profile
            style2: Second style profile
            
        Returns:
            Compatibility score between 0 and 1 (higher = more compatible)
        """
        # Calculate differences in key dimensions
        tone_diff = (
            abs(style1.tone.warmth - style2.tone.warmth) +
            abs(style1.tone.formality - style2.tone.formality) +
            abs(style1.tone.humor - style2.tone.humor)
        ) / 3.0
        
        stance_diff = abs(style1.stance.assertiveness - style2.stance.assertiveness)
        
        pacing_diff = abs(style1.pacing.expansiveness - style2.pacing.expansiveness)
        
        # Calculate overall compatibility
        total_diff = (tone_diff + stance_diff + pacing_diff) / 3.0
        
        # Convert to compatibility score (1 - difference)
        compatibility = max(0.0, 1.0 - total_diff)
        
        return compatibility