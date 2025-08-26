"""
Tests for style mode selection functionality.

This module tests the style synthesizer's mode selection and decoding parameter generation.
"""

import pytest
from datetime import datetime

from pmx.style import StyleSynthesizer
from pmx.models import PMXConfig, TraitWeights, AffectSnapshot, StyleMode


class TestStyleModeSelection:
    """Test style mode selection and synthesis."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PMXConfig(
            style_adaptation_rate=0.3,
        )
    
    @pytest.fixture
    def style_synthesizer(self, config):
        """Create a Style Synthesizer instance."""
        return StyleSynthesizer(config)
    
    @pytest.fixture
    def baseline_weights(self):
        """Create baseline trait weights."""
        return TraitWeights(
            creative=0.5,
            analytical=0.5,
            empathic=0.5,
            curiosity=0.5,
            balance=0.5,
        )
    
    @pytest.fixture
    def baseline_affect(self):
        """Create baseline affect snapshot."""
        return AffectSnapshot(
            arousal=0.5,
            valence=0.0,
            stress=0.2,
            tags=["baseline"],
        )
    
    def test_synthesize_mode_flow_creative(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test synthesizing FLOW mode for creative context."""
        context = {
            "task_type": "creative",
            "audience": "friend",
            "urgency": "low",
        }
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Should select FLOW mode for creative tasks
        assert style_mode.mode == "FLOW"
        assert style_mode.temperature > 0.7  # FLOW mode has high temperature
        assert style_mode.creativity_boost > 0.2  # Should boost creativity
    
    def test_synthesize_mode_deep_analytical(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test synthesizing DEEP mode for analytical context."""
        context = {
            "task_type": "analytical",
            "audience": "professional",
            "urgency": "normal",
        }
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Should select DEEP mode for analytical tasks
        assert style_mode.mode == "DEEP"
        assert style_mode.temperature < 0.6  # DEEP mode has lower temperature
        assert style_mode.analytical_boost > 0.3  # Should boost analytical thinking
    
    def test_synthesize_mode_crisis_urgent(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test synthesizing CRISIS mode for urgent context."""
        context = {
            "task_type": "problem_solving",
            "audience": "professional",
            "urgency": "high",
        }
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Should select CRISIS mode for urgent tasks
        assert style_mode.mode == "CRISIS"
        assert style_mode.temperature < 0.4  # CRISIS mode has low temperature
        assert style_mode.max_tokens < 1000  # CRISIS mode has shorter responses
        assert style_mode.analytical_boost > 0.5  # Should boost analytical thinking
    
    def test_synthesize_mode_high_creative_trait(self, style_synthesizer, baseline_affect):
        """Test synthesizing mode with high creative trait."""
        high_creative_weights = TraitWeights(
            creative=0.9,
            analytical=0.3,
            empathic=0.5,
            curiosity=0.7,
            balance=0.4,
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(high_creative_weights, baseline_affect, context)
        
        # High creative trait should boost creativity and temperature
        assert style_mode.creativity_boost > 0.3
        assert style_mode.temperature > 0.6
    
    def test_synthesize_mode_high_analytical_trait(self, style_synthesizer, baseline_affect):
        """Test synthesizing mode with high analytical trait."""
        high_analytical_weights = TraitWeights(
            creative=0.3,
            analytical=0.9,
            empathic=0.4,
            curiosity=0.5,
            balance=0.7,
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(high_analytical_weights, baseline_affect, context)
        
        # High analytical trait should boost analytical thinking and reduce temperature
        assert style_mode.analytical_boost > 0.4
        assert style_mode.temperature < 0.6
        assert style_mode.repetition_penalty > 1.1
    
    def test_synthesize_mode_high_empathic_trait(self, style_synthesizer, baseline_affect):
        """Test synthesizing mode with high empathic trait."""
        high_empathic_weights = TraitWeights(
            creative=0.4,
            analytical=0.5,
            empathic=0.9,
            curiosity=0.6,
            balance=0.5,
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(high_empathic_weights, baseline_affect, context)
        
        # High empathic trait should boost empathy
        assert style_mode.empathy_boost > 0.4
    
    def test_synthesize_mode_high_arousal_affect(self, style_synthesizer, baseline_weights):
        """Test synthesizing mode with high arousal affect."""
        high_arousal_affect = AffectSnapshot(
            arousal=0.8,
            valence=0.5,
            stress=0.3,
            tags=["excited"],
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, high_arousal_affect, context)
        
        # High arousal should boost creativity and temperature
        assert style_mode.creativity_boost > 0.2
        assert style_mode.temperature > 0.6
        assert style_mode.max_tokens > 1200  # Should allow longer responses
    
    def test_synthesize_mode_low_arousal_affect(self, style_synthesizer, baseline_weights):
        """Test synthesizing mode with low arousal affect."""
        low_arousal_affect = AffectSnapshot(
            arousal=0.2,
            valence=0.3,
            stress=0.2,
            tags=["calm"],
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, low_arousal_affect, context)
        
        # Low arousal should boost analytical thinking and reduce temperature
        assert style_mode.analytical_boost > 0.2
        assert style_mode.temperature < 0.6
        assert style_mode.max_tokens < 1500  # Should allow shorter responses
    
    def test_synthesize_mode_high_stress_affect(self, style_synthesizer, baseline_weights):
        """Test synthesizing mode with high stress affect."""
        high_stress_affect = AffectSnapshot(
            arousal=0.6,
            valence=-0.2,
            stress=0.8,
            tags=["stressed"],
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, high_stress_affect, context)
        
        # High stress should boost analytical thinking and reduce temperature
        assert style_mode.analytical_boost > 0.4
        assert style_mode.temperature < 0.5
        assert style_mode.max_tokens < 1000  # Should allow shorter responses
        assert style_mode.repetition_penalty > 1.2
    
    def test_synthesize_mode_positive_valence_affect(self, style_synthesizer, baseline_weights):
        """Test synthesizing mode with positive valence affect."""
        positive_valence_affect = AffectSnapshot(
            arousal=0.5,
            valence=0.7,
            stress=0.2,
            tags=["positive"],
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, positive_valence_affect, context)
        
        # Positive valence should boost empathy and creativity
        assert style_mode.empathy_boost > 0.2
        assert style_mode.creativity_boost > 0.2
        assert style_mode.temperature > 0.5
    
    def test_synthesize_mode_negative_valence_affect(self, style_synthesizer, baseline_weights):
        """Test synthesizing mode with negative valence affect."""
        negative_valence_affect = AffectSnapshot(
            arousal=0.4,
            valence=-0.6,
            stress=0.4,
            tags=["negative"],
        )
        
        context = {"task_type": "general"}
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, negative_valence_affect, context)
        
        # Negative valence should boost analytical thinking
        assert style_mode.analytical_boost > 0.2
        assert style_mode.temperature < 0.6
    
    def test_audience_adjustments_professional(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test audience adjustments for professional context."""
        context = {"audience": "professional"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Professional audience should reduce temperature and increase formality
        assert style_mode.temperature < 0.7
        # Note: formality is not directly exposed in StyleMode, but should affect other parameters
    
    def test_audience_adjustments_friend(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test audience adjustments for friend context."""
        context = {"audience": "friend"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Friend audience should increase empathy and temperature
        assert style_mode.empathy_boost > 0.3
        assert style_mode.temperature > 0.6
    
    def test_audience_adjustments_child(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test audience adjustments for child context."""
        context = {"audience": "child"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Child audience should increase empathy, creativity, and temperature
        assert style_mode.empathy_boost > 0.4
        assert style_mode.creativity_boost > 0.3
        assert style_mode.temperature > 0.7
        assert style_mode.max_tokens < 1200  # Should limit response length
    
    def test_channel_adjustments_email(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test channel adjustments for email context."""
        context = {"channel": "email"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Email should increase formality and limit length
        assert style_mode.max_tokens < 2500
        assert style_mode.analytical_boost > 0.2
    
    def test_channel_adjustments_chat(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test channel adjustments for chat context."""
        context = {"channel": "chat"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Chat should increase temperature and limit length
        assert style_mode.temperature > 0.6
        assert style_mode.max_tokens < 1000
    
    def test_channel_adjustments_document(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test channel adjustments for document context."""
        context = {"channel": "document"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Document should increase analytical thinking and formality
        assert style_mode.analytical_boost > 0.3
        assert style_mode.max_tokens > 2000  # Should allow longer responses
    
    def test_time_pressure_adjustments_high(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test time pressure adjustments for high urgency."""
        context = {"time_pressure": "high"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # High time pressure should reduce length and temperature
        assert style_mode.max_tokens < 1200
        assert style_mode.temperature < 0.6
    
    def test_time_pressure_adjustments_low(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test time pressure adjustments for low urgency."""
        context = {"time_pressure": "low"}
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Low time pressure should increase creativity and length
        assert style_mode.creativity_boost > 0.2
        assert style_mode.max_tokens > 1500
    
    def test_parameter_clamping(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test that parameters are properly clamped to valid ranges."""
        # Create extreme weights that would push parameters out of bounds
        extreme_weights = TraitWeights(
            creative=1.0,
            analytical=1.0,
            empathic=1.0,
            curiosity=1.0,
            balance=1.0,
        )
        
        context = {"task_type": "creative", "audience": "child", "urgency": "low"}
        style_mode = style_synthesizer.synthesize_mode(extreme_weights, baseline_affect, context)
        
        # All parameters should be within valid ranges
        assert 0.1 <= style_mode.temperature <= 2.0
        assert 0.1 <= style_mode.top_p <= 1.0
        assert 100 <= style_mode.max_tokens <= 4000
        assert 0.5 <= style_mode.repetition_penalty <= 2.0
        assert 0.0 <= style_mode.creativity_boost <= 1.0
        assert 0.0 <= style_mode.analytical_boost <= 1.0
        assert 0.0 <= style_mode.empathy_boost <= 1.0
    
    def test_mode_recommendation(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test mode recommendation with explanation."""
        context = {"task_type": "creative", "audience": "friend"}
        
        recommendation = style_synthesizer.get_mode_recommendation(baseline_weights, baseline_affect, context)
        
        assert "recommended_mode" in recommendation
        assert "mode_scores" in recommendation
        assert "explanation" in recommendation
        assert "confidence" in recommendation
        
        assert recommendation["recommended_mode"] in ["FLOW", "DEEP", "CRISIS"]
        assert len(recommendation["mode_scores"]) == 3
        assert 0.0 <= recommendation["confidence"] <= 1.0
        assert len(recommendation["explanation"]) > 0
    
    def test_mode_scores_calculation(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test mode scores calculation."""
        context = {"task_type": "analytical"}
        
        mode_scores = style_synthesizer._calculate_mode_scores(baseline_weights, baseline_affect, context)
        
        assert "FLOW" in mode_scores
        assert "DEEP" in mode_scores
        assert "CRISIS" in mode_scores
        
        # All scores should be non-negative
        assert all(score >= 0.0 for score in mode_scores.values())
        
        # At least one mode should have a positive score
        assert any(score > 0.0 for score in mode_scores.values())
    
    def test_complex_context_combination(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test mode synthesis with complex context combination."""
        context = {
            "task_type": "problem_solving",
            "audience": "professional",
            "urgency": "high",
            "channel": "email",
            "time_pressure": "high",
        }
        
        style_mode = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Complex context should result in appropriate mode selection
        assert style_mode.mode in ["DEEP", "CRISIS"]  # Should favor analytical modes
        
        # Should reflect all context factors
        assert style_mode.temperature < 0.6  # Professional + high urgency
        assert style_mode.analytical_boost > 0.3  # Problem solving + professional
        assert style_mode.max_tokens < 2500  # Email + high time pressure
    
    def test_consistency_for_same_context(self, style_synthesizer, baseline_weights, baseline_affect):
        """Test that mode synthesis is consistent for the same context."""
        context = {"task_type": "creative", "audience": "friend"}
        
        style_mode1 = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        style_mode2 = style_synthesizer.synthesize_mode(baseline_weights, baseline_affect, context)
        
        # Should be consistent (within small floating point differences)
        assert abs(style_mode1.temperature - style_mode2.temperature) < 0.001
        assert abs(style_mode1.top_p - style_mode2.top_p) < 0.001
        assert style_mode1.max_tokens == style_mode2.max_tokens
        assert abs(style_mode1.repetition_penalty - style_mode2.repetition_penalty) < 0.001
        assert abs(style_mode1.creativity_boost - style_mode2.creativity_boost) < 0.001
        assert abs(style_mode1.analytical_boost - style_mode2.analytical_boost) < 0.001
        assert abs(style_mode1.empathy_boost - style_mode2.empathy_boost) < 0.001