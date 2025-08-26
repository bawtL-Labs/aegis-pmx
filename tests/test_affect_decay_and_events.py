"""
Tests for affect decay and event-driven updates.

This module tests the affect engine's decay mechanism and event impact handling.
"""

import pytest
from datetime import datetime, timedelta

from pmx.affect import AffectEngine
from pmx.models import PMXConfig, AffectSnapshot


class TestAffectDecayAndEvents:
    """Test affect decay and event-driven updates."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PMXConfig(
            affect_decay_rate=0.95,
            arousal_setpoint=0.5,
            valence_setpoint=0.0,
            stress_setpoint=0.2,
        )
    
    @pytest.fixture
    def affect_engine(self, config):
        """Create an Affect Engine instance."""
        return AffectEngine(config)
    
    @pytest.fixture
    def baseline_affect(self):
        """Create a baseline affect snapshot."""
        return AffectSnapshot(
            arousal=0.5,
            valence=0.0,
            stress=0.2,
            tags=["baseline"],
        )
    
    def test_apply_decay_baseline(self, affect_engine, baseline_affect):
        """Test applying decay to baseline affect."""
        decayed = affect_engine.apply_decay(baseline_affect)
        
        # Decay should move values toward setpoints
        assert abs(decayed.arousal - 0.5) < 0.1  # Should stay near setpoint
        assert abs(decayed.valence - 0.0) < 0.1  # Should stay near setpoint
        assert abs(decayed.stress - 0.2) < 0.1   # Should stay near setpoint
        
        # Timestamp should be updated
        assert decayed.timestamp > baseline_affect.timestamp
    
    def test_apply_decay_high_arousal(self, affect_engine):
        """Test applying decay to high arousal affect."""
        high_arousal = AffectSnapshot(
            arousal=0.9,
            valence=0.5,
            stress=0.3,
            tags=["excited"],
        )
        
        decayed = affect_engine.apply_decay(high_arousal)
        
        # Arousal should decrease toward setpoint
        assert decayed.arousal < high_arousal.arousal
        assert decayed.arousal > 0.4  # Should not decay too much in one step
    
    def test_apply_decay_low_arousal(self, affect_engine):
        """Test applying decay to low arousal affect."""
        low_arousal = AffectSnapshot(
            arousal=0.1,
            valence=-0.3,
            stress=0.1,
            tags=["calm"],
        )
        
        decayed = affect_engine.apply_decay(low_arousal)
        
        # Arousal should increase toward setpoint
        assert decayed.arousal > low_arousal.arousal
        assert decayed.arousal < 0.6  # Should not increase too much in one step
    
    def test_apply_decay_high_stress(self, affect_engine):
        """Test applying decay to high stress affect."""
        high_stress = AffectSnapshot(
            arousal=0.7,
            valence=-0.4,
            stress=0.8,
            tags=["stressed"],
        )
        
        decayed = affect_engine.apply_decay(high_stress)
        
        # Stress should decrease toward setpoint
        assert decayed.stress < high_stress.stress
        assert decayed.stress > 0.3  # Should not decay too much in one step
    
    def test_apply_decay_positive_valence(self, affect_engine):
        """Test applying decay to positive valence affect."""
        positive_valence = AffectSnapshot(
            arousal=0.6,
            valence=0.7,
            stress=0.2,
            tags=["positive"],
        )
        
        decayed = affect_engine.apply_decay(positive_valence)
        
        # Valence should decrease toward setpoint
        assert decayed.valence < positive_valence.valence
        assert decayed.valence > 0.2  # Should not decay too much in one step
    
    def test_apply_decay_negative_valence(self, affect_engine):
        """Test applying decay to negative valence affect."""
        negative_valence = AffectSnapshot(
            arousal=0.4,
            valence=-0.6,
            stress=0.4,
            tags=["negative"],
        )
        
        decayed = affect_engine.apply_decay(negative_valence)
        
        # Valence should increase toward setpoint
        assert decayed.valence > negative_valence.valence
        assert decayed.valence < -0.2  # Should not increase too much in one step
    
    def test_calculate_event_impact_plan_start(self, affect_engine):
        """Test calculating impact for plan start event."""
        impact = affect_engine.calculate_event_impact("plan:start", intensity=1.0)
        
        assert "arousal" in impact
        assert "valence" in impact
        assert "stress" in impact
        
        # Plan start should increase arousal and stress
        assert impact["arousal"] > 0
        assert impact["stress"] > 0
    
    def test_calculate_event_impact_plan_complete(self, affect_engine):
        """Test calculating impact for plan complete event."""
        impact = affect_engine.calculate_event_impact("plan:complete", intensity=1.0)
        
        # Plan complete should increase valence and decrease stress
        assert impact["valence"] > 0
        assert impact["stress"] < 0
    
    def test_calculate_event_impact_plan_fail(self, affect_engine):
        """Test calculating impact for plan fail event."""
        impact = affect_engine.calculate_event_impact("plan:fail", intensity=1.0)
        
        # Plan fail should decrease valence and increase stress
        assert impact["valence"] < 0
        assert impact["stress"] > 0
    
    def test_calculate_event_impact_tool_success(self, affect_engine):
        """Test calculating impact for tool success event."""
        impact = affect_engine.calculate_event_impact("tool:success", intensity=1.0)
        
        # Tool success should slightly increase valence and decrease stress
        assert impact["valence"] > 0
        assert impact["stress"] < 0
    
    def test_calculate_event_impact_tool_fail(self, affect_engine):
        """Test calculating impact for tool fail event."""
        impact = affect_engine.calculate_event_impact("tool:fail", intensity=1.0)
        
        # Tool fail should decrease valence and increase stress
        assert impact["valence"] < 0
        assert impact["stress"] > 0
    
    def test_calculate_event_impact_success(self, affect_engine):
        """Test calculating impact for success event."""
        impact = affect_engine.calculate_event_impact("success", intensity=1.0)
        
        # Success should increase valence and decrease stress
        assert impact["valence"] > 0
        assert impact["stress"] < 0
    
    def test_calculate_event_impact_failure(self, affect_engine):
        """Test calculating impact for failure event."""
        impact = affect_engine.calculate_event_impact("failure", intensity=1.0)
        
        # Failure should decrease valence and increase stress
        assert impact["valence"] < 0
        assert impact["stress"] > 0
    
    def test_calculate_event_impact_intensity_scaling(self, affect_engine):
        """Test that event impact scales with intensity."""
        impact_low = affect_engine.calculate_event_impact("success", intensity=0.5)
        impact_high = affect_engine.calculate_event_impact("success", intensity=1.0)
        
        # Higher intensity should have greater impact
        assert abs(impact_high["valence"]) > abs(impact_low["valence"])
        assert abs(impact_high["stress"]) > abs(impact_low["stress"])
    
    def test_apply_event_impact_plan_start(self, affect_engine, baseline_affect):
        """Test applying plan start event impact."""
        updated = affect_engine.apply_event_impact(baseline_affect, "plan:start", intensity=1.0)
        
        # Should increase arousal and stress
        assert updated.arousal > baseline_affect.arousal
        assert updated.stress > baseline_affect.stress
        
        # Values should be clamped to valid ranges
        assert 0.0 <= updated.arousal <= 1.0
        assert 0.0 <= updated.stress <= 1.0
        assert -1.0 <= updated.valence <= 1.0
    
    def test_apply_event_impact_plan_complete(self, affect_engine, baseline_affect):
        """Test applying plan complete event impact."""
        updated = affect_engine.apply_event_impact(baseline_affect, "plan:complete", intensity=1.0)
        
        # Should increase valence and decrease stress
        assert updated.valence > baseline_affect.valence
        assert updated.stress < baseline_affect.stress
    
    def test_apply_event_impact_creative_flow(self, affect_engine, baseline_affect):
        """Test applying creative flow event impact."""
        updated = affect_engine.apply_event_impact(baseline_affect, "creative:flow", intensity=1.0)
        
        # Should increase arousal and valence, decrease stress
        assert updated.arousal > baseline_affect.arousal
        assert updated.valence > baseline_affect.valence
        assert updated.stress < baseline_affect.stress
    
    def test_apply_event_impact_learning_breakthrough(self, affect_engine, baseline_affect):
        """Test applying learning breakthrough event impact."""
        updated = affect_engine.apply_event_impact(baseline_affect, "learning:breakthrough", intensity=1.0)
        
        # Should increase arousal and valence, decrease stress
        assert updated.arousal > baseline_affect.arousal
        assert updated.valence > baseline_affect.valence
        assert updated.stress < baseline_affect.stress
    
    def test_apply_event_impact_social_conflict(self, affect_engine, baseline_affect):
        """Test applying social conflict event impact."""
        updated = affect_engine.apply_event_impact(baseline_affect, "social:conflict", intensity=1.0)
        
        # Should increase arousal and stress, decrease valence
        assert updated.arousal > baseline_affect.arousal
        assert updated.stress > baseline_affect.stress
        assert updated.valence < baseline_affect.valence
    
    def test_state_interactions_high_arousal_high_valence(self, affect_engine):
        """Test state interactions for high arousal and high valence."""
        # Create affect with high arousal and high valence
        affect = AffectSnapshot(
            arousal=0.8,
            valence=0.6,
            stress=0.2,
            tags=["excited"],
        )
        
        updated = affect_engine.apply_event_impact(affect, "general", intensity=0.0)
        
        # High arousal + high valence should boost valence further
        assert updated.valence > affect.valence
    
    def test_state_interactions_high_arousal_low_valence(self, affect_engine):
        """Test state interactions for high arousal and low valence."""
        # Create affect with high arousal and low valence
        affect = AffectSnapshot(
            arousal=0.8,
            valence=-0.6,
            stress=0.3,
            tags=["anxious"],
        )
        
        updated = affect_engine.apply_event_impact(affect, "general", intensity=0.0)
        
        # High arousal + low valence should decrease valence further
        assert updated.valence < affect.valence
    
    def test_state_interactions_high_stress(self, affect_engine):
        """Test state interactions for high stress."""
        # Create affect with high stress
        affect = AffectSnapshot(
            arousal=0.6,
            valence=-0.2,
            stress=0.8,
            tags=["stressed"],
        )
        
        updated = affect_engine.apply_event_impact(affect, "general", intensity=0.0)
        
        # High stress should increase arousal and decrease valence
        assert updated.arousal > affect.arousal
        assert updated.valence < affect.valence
    
    def test_affect_stability_score(self, affect_engine):
        """Test affect stability score calculation."""
        # Test stable affect (near setpoints)
        stable_affect = AffectSnapshot(
            arousal=0.5,  # At setpoint
            valence=0.0,  # At setpoint
            stress=0.2,   # At setpoint
            tags=["stable"],
        )
        
        stability = affect_engine.get_affect_stability_score(stable_affect)
        assert stability > 0.8  # Should be very stable
        
        # Test unstable affect (far from setpoints)
        unstable_affect = AffectSnapshot(
            arousal=0.9,  # Far from setpoint
            valence=0.8,  # Far from setpoint
            stress=0.8,   # Far from setpoint
            tags=["unstable"],
        )
        
        stability = affect_engine.get_affect_stability_score(unstable_affect)
        assert stability < 0.5  # Should be less stable
    
    def test_affect_tags_update(self, affect_engine):
        """Test that affect tags are updated based on values."""
        # Test high arousal
        high_arousal = AffectSnapshot(
            arousal=0.8,
            valence=0.5,
            stress=0.3,
            tags=[],
        )
        
        updated = affect_engine.apply_event_impact(high_arousal, "general", intensity=0.0)
        assert "excited" in updated.tags or "energetic" in updated.tags
        
        # Test low valence
        low_valence = AffectSnapshot(
            arousal=0.4,
            valence=-0.7,
            stress=0.3,
            tags=[],
        )
        
        updated = affect_engine.apply_event_impact(low_valence, "general", intensity=0.0)
        assert "sad" in updated.tags or "negative" in updated.tags
        
        # Test high stress
        high_stress = AffectSnapshot(
            arousal=0.6,
            valence=-0.2,
            stress=0.8,
            tags=[],
        )
        
        updated = affect_engine.apply_event_impact(high_stress, "general", intensity=0.0)
        assert "stressed" in updated.tags or "overwhelmed" in updated.tags
    
    def test_multiple_event_impacts(self, affect_engine, baseline_affect):
        """Test applying multiple event impacts in sequence."""
        # Apply plan start
        updated = affect_engine.apply_event_impact(baseline_affect, "plan:start", intensity=1.0)
        
        # Apply tool success
        updated = affect_engine.apply_event_impact(updated, "tool:success", intensity=0.8)
        
        # Apply plan complete
        updated = affect_engine.apply_event_impact(updated, "plan:complete", intensity=1.0)
        
        # Final state should reflect all impacts
        assert updated.arousal > baseline_affect.arousal  # From plan start
        assert updated.valence > baseline_affect.valence  # From tool success and plan complete
        assert updated.stress < baseline_affect.stress    # From plan complete
    
    def test_event_impact_clamping(self, affect_engine):
        """Test that event impacts are properly clamped to valid ranges."""
        # Start with extreme values
        extreme_affect = AffectSnapshot(
            arousal=0.9,
            valence=0.9,
            stress=0.9,
            tags=["extreme"],
        )
        
        # Apply a strong positive event
        updated = affect_engine.apply_event_impact(extreme_affect, "success", intensity=1.0)
        
        # Values should be clamped to valid ranges
        assert 0.0 <= updated.arousal <= 1.0
        assert -1.0 <= updated.valence <= 1.0
        assert 0.0 <= updated.stress <= 1.0