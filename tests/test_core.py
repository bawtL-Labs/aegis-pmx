"""
Tests for the core PersonalityMatrix class.

This module contains comprehensive tests for the main PersonalityMatrix
class and its core functionality.
"""

import pytest
import asyncio
from datetime import datetime

from sam.persona.core import PersonalityMatrix
from sam.persona.models import (
    PersonalityConfig,
    StateUpdate,
    EventType,
    AudienceContext,
    ChannelContext,
    AudienceType,
    ChannelType,
)


class TestPersonalityMatrix:
    """Test cases for the PersonalityMatrix class."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PersonalityConfig(
            state_decay_rate=0.9,
            valence_setpoint=0.5,
            arousal_setpoint=0.4,
            drift_threshold=0.3,
        )
    
    @pytest.fixture
    def pmx(self, config):
        """Create a PersonalityMatrix instance."""
        return PersonalityMatrix(config)
    
    def test_initialization(self, pmx):
        """Test that the personality matrix initializes correctly."""
        assert pmx is not None
        assert pmx.traits is not None
        assert pmx.state_engine is not None
        assert pmx.style_synthesizer is not None
        assert pmx.boundary_manager is not None
        assert pmx.memory_lenser is not None
        assert pmx.observability is not None
    
    def test_get_traits(self, pmx):
        """Test getting the trait kernel."""
        traits = pmx.get_traits()
        assert traits is not None
        assert hasattr(traits, 'curiosity')
        assert hasattr(traits, 'balance')
        assert hasattr(traits, 'wit')
        assert hasattr(traits, 'candor')
        assert hasattr(traits, 'care')
    
    def test_get_current_state(self, pmx):
        """Test getting the current affective state."""
        state = pmx.get_current_state()
        assert state is not None
        assert hasattr(state, 'valence')
        assert hasattr(state, 'arousal')
        assert hasattr(state, 'fatigue')
        assert hasattr(state, 'tags')
        assert hasattr(state, 'decay')
    
    def test_get_style_profile(self, pmx):
        """Test getting the current style profile."""
        style = pmx.get_style_profile()
        assert style is not None
        assert hasattr(style, 'tone')
        assert hasattr(style, 'diction')
        assert hasattr(style, 'pacing')
        assert hasattr(style, 'stance')
        assert hasattr(style, 'boundaries')
        assert hasattr(style, 'decoding')
    
    def test_get_boundary_caps(self, pmx):
        """Test getting the current boundary caps."""
        boundaries = pmx.get_boundary_caps()
        assert boundaries is not None
        assert hasattr(boundaries, 'max_flirtation')
        assert hasattr(boundaries, 'max_humor')
        assert hasattr(boundaries, 'max_candor')
        assert hasattr(boundaries, 'min_formality')
        assert hasattr(boundaries, 'safety_tags')
    
    def test_get_decoding_profile(self, pmx):
        """Test getting the current decoding profile."""
        decoding = pmx.get_decoding_profile()
        assert decoding is not None
        assert hasattr(decoding, 'temp')
        assert hasattr(decoding, 'top_p')
        assert hasattr(decoding, 'top_k')
        assert hasattr(decoding, 'penalty')
        assert hasattr(decoding, 'max_tokens')
    
    @pytest.mark.asyncio
    async def test_update_state_positive_interaction(self, pmx):
        """Test updating state with a positive interaction."""
        initial_state = pmx.get_current_state()
        
        update = StateUpdate(
            event_type=EventType.POSITIVE_INTERACTION,
            intensity=0.8,
            context={"test": True},
        )
        
        new_style = await pmx.update_state(update)
        new_state = pmx.get_current_state()
        
        assert new_style is not None
        assert new_state is not None
        # Positive interaction should increase valence
        assert new_state.valence > initial_state.valence
    
    @pytest.mark.asyncio
    async def test_update_state_negative_interaction(self, pmx):
        """Test updating state with a negative interaction."""
        initial_state = pmx.get_current_state()
        
        update = StateUpdate(
            event_type=EventType.NEGATIVE_INTERACTION,
            intensity=0.7,
            context={"test": True},
        )
        
        new_style = await pmx.update_state(update)
        new_state = pmx.get_current_state()
        
        assert new_style is not None
        assert new_state is not None
        # Negative interaction should decrease valence
        assert new_state.valence < initial_state.valence
    
    @pytest.mark.asyncio
    async def test_update_state_with_audience(self, pmx):
        """Test updating state with audience context."""
        update = StateUpdate(
            event_type=EventType.SOCIAL,
            intensity=0.6,
            audience=AudienceContext(
                type=AudienceType.FRIEND,
                name="Test Friend",
            ),
            context={"test": True},
        )
        
        new_style = await pmx.update_state(update)
        
        assert new_style is not None
        # Friend audience should increase warmth
        assert new_style.tone.warmth > 0.5
    
    @pytest.mark.asyncio
    async def test_update_state_with_channel(self, pmx):
        """Test updating state with channel context."""
        update = StateUpdate(
            event_type=EventType.LEARNING,
            intensity=0.5,
            channel=ChannelContext(
                type=ChannelType.EMAIL,
                platform="test",
            ),
            context={"test": True},
        )
        
        new_style = await pmx.update_state(update)
        
        assert new_style is not None
        # Email channel should increase formality
        assert new_style.tone.formality > 0.5
    
    @pytest.mark.asyncio
    async def test_reset_to_baseline(self, pmx):
        """Test resetting to baseline state."""
        # First update the state
        update = StateUpdate(
            event_type=EventType.STRESS,
            intensity=0.8,
        )
        await pmx.update_state(update)
        
        # Reset to baseline
        baseline_style = await pmx.reset_to_baseline()
        baseline_state = pmx.get_current_state()
        
        assert baseline_style is not None
        assert baseline_state is not None
        # Should be close to setpoints
        assert abs(baseline_state.valence - pmx.config.valence_setpoint) < 0.1
        assert abs(baseline_state.arousal - pmx.config.arousal_setpoint) < 0.1
    
    def test_get_recent_traces(self, pmx):
        """Test getting recent traces."""
        traces = pmx.get_recent_traces(5)
        assert isinstance(traces, list)
        assert len(traces) <= 5
    
    def test_get_style_history(self, pmx):
        """Test getting style history."""
        history = pmx.get_style_history(24)
        assert isinstance(history, list)
    
    def test_export_personality(self, pmx):
        """Test exporting personality state."""
        export_data = pmx.export_personality()
        assert isinstance(export_data, dict)
        assert "traits" in export_data
        assert "current_state" in export_data
        assert "current_style" in export_data
        assert "current_boundaries" in export_data
        assert "config" in export_data
        assert "export_timestamp" in export_data
    
    def test_import_personality(self, pmx):
        """Test importing personality state."""
        # Export current state
        export_data = pmx.export_personality()
        
        # Modify the export data
        export_data["current_state"]["valence"] = 0.8
        
        # Import the modified data
        pmx.import_personality(export_data)
        
        # Check that the state was updated
        new_state = pmx.get_current_state()
        assert new_state.valence == 0.8
    
    @pytest.mark.asyncio
    async def test_apply_memory_lensing(self, pmx):
        """Test applying memory lensing."""
        content = "This is a positive and warm interaction with a friend."
        lenses = await pmx.apply_memory_lensing(content, "interaction")
        
        assert isinstance(lenses, dict)
        assert len(lenses) > 0
        # Should have positive and social lenses
        assert any("positive" in lens.lower() or "warm" in lens.lower() for lens in lenses.keys())
    
    def test_get_personality_summary(self, pmx):
        """Test getting personality summary."""
        summary = pmx.get_personality_summary()
        assert isinstance(summary, dict)
        assert "traits" in summary
        assert "current_mood" in summary
        assert "communication_style" in summary
        assert "boundaries" in summary
        assert "llm_settings" in summary
    
    @pytest.mark.asyncio
    async def test_drift_detection(self, pmx):
        """Test personality drift detection."""
        # Make a large state change that should trigger drift detection
        update = StateUpdate(
            event_type=EventType.SURPRISE,
            intensity=1.0,  # Maximum intensity
            context={"drastic_change": True},
        )
        
        new_style = await pmx.update_state(update)
        
        # Check if drift was detected (this depends on the drift threshold)
        traces = pmx.get_recent_traces(1)
        if traces:
            # The trace should contain information about the change
            assert traces[0].style_delta is not None
    
    def test_invalid_import_data(self, pmx):
        """Test importing invalid personality data."""
        invalid_data = {
            "traits": {"invalid": "data"},
            "current_state": {"invalid": "state"},
        }
        
        with pytest.raises(ValueError):
            pmx.import_personality(invalid_data)
    
    @pytest.mark.asyncio
    async def test_multiple_state_updates(self, pmx):
        """Test multiple consecutive state updates."""
        updates = [
            StateUpdate(event_type=EventType.POSITIVE_INTERACTION, intensity=0.5),
            StateUpdate(event_type=EventType.LEARNING, intensity=0.3),
            StateUpdate(event_type=EventType.CREATIVITY, intensity=0.7),
        ]
        
        for update in updates:
            style = await pmx.update_state(update)
            assert style is not None
        
        # Check that we have traces for all updates
        traces = pmx.get_recent_traces(10)
        assert len(traces) >= len(updates)
    
    def test_config_override(self):
        """Test that configuration overrides work correctly."""
        custom_config = PersonalityConfig(
            state_decay_rate=0.8,
            valence_setpoint=0.7,
            arousal_setpoint=0.6,
            drift_threshold=0.1,
        )
        
        pmx = PersonalityMatrix(custom_config)
        
        # Check that custom config was applied
        assert pmx.config.state_decay_rate == 0.8
        assert pmx.config.valence_setpoint == 0.7
        assert pmx.config.arousal_setpoint == 0.6
        assert pmx.config.drift_threshold == 0.1