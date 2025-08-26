"""
Tests for boundary policy hints functionality.

This module tests the boundary manager's policy hint generation and condition handling.
"""

import pytest
from datetime import datetime, timedelta

from pmx.boundary import BoundaryManager
from pmx.models import PMXConfig, BoundaryCondition, PolicyHint


class TestBoundaryPolicyHints:
    """Test boundary policy hints functionality."""
    
    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PMXConfig(
            boundary_check_interval=5.0,
        )
    
    @pytest.fixture
    def boundary_manager(self, config):
        """Create a Boundary Manager instance."""
        return BoundaryManager(config)
    
    def test_get_conditions_external_post(self, boundary_manager):
        """Test getting conditions for external post context."""
        context = {
            "action_type": "external_post",
            "min_interval_seconds": 600,
            "max_posts_per_hour": 6,
        }
        
        conditions = boundary_manager.get_conditions(context)
        
        # Should find external post cooldown condition
        assert len(conditions) > 0
        external_post_condition = next(
            (c for c in conditions if c["condition_id"] == "external_post_cooldown"), None
        )
        assert external_post_condition is not None
        assert external_post_condition["reason"] == "Prevent spam and maintain quality of external communications"
    
    def test_get_conditions_complex_topic(self, boundary_manager):
        """Test getting conditions for complex topic context."""
        context = {
            "topic_complexity": "high",
            "audience_expertise": "low",
            "content_length": "long",
        }
        
        conditions = boundary_manager.get_conditions(context)
        
        # Should find summary requirement condition
        assert len(conditions) > 0
        summary_condition = next(
            (c for c in conditions if c["condition_id"] == "require_summary"), None
        )
        assert summary_condition is not None
        assert summary_condition["reason"] == "Ensure complex topics are properly summarized before detailed discussion"
    
    def test_get_conditions_high_stress(self, boundary_manager):
        """Test getting conditions for high stress context."""
        context = {
            "stress_level": "high",
            "decision_impact": "high",
            "time_pressure": "high",
        }
        
        conditions = boundary_manager.get_conditions(context)
        
        # Should find high stress protection condition
        assert len(conditions) > 0
        stress_condition = next(
            (c for c in conditions if c["condition_id"] == "high_stress_protection"), None
        )
        assert stress_condition is not None
        assert stress_condition["reason"] == "Protect against poor decisions during high stress periods"
    
    def test_get_conditions_creative_flow(self, boundary_manager):
        """Test getting conditions for creative flow context."""
        context = {
            "creative_flow": "active",
            "interruption_type": "non_urgent",
            "flow_duration": "recent",
        }
        
        conditions = boundary_manager.get_conditions(context)
        
        # Should find creative flow protection condition
        assert len(conditions) > 0
        flow_condition = next(
            (c for c in conditions if c["condition_id"] == "creative_flow_protection"), None
        )
        assert flow_condition is not None
        assert flow_condition["reason"] == "Protect creative flow states from interruption"
    
    def test_get_conditions_learning_mode(self, boundary_manager):
        """Test getting conditions for learning mode context."""
        context = {
            "learning_mode": "active",
            "session_duration": "recent",
            "interruption_type": "distracting",
        }
        
        conditions = boundary_manager.get_conditions(context)
        
        # Should find learning mode protection condition
        assert len(conditions) > 0
        learning_condition = next(
            (c for c in conditions if c["condition_id"] == "learning_mode_protection"), None
        )
        assert learning_condition is not None
        assert learning_condition["reason"] == "Protect learning sessions from interruption"
    
    def test_get_conditions_social_interaction(self, boundary_manager):
        """Test getting conditions for social interaction context."""
        context = {
            "interaction_type": "social",
            "frequency": "high",
            "duration": "extended",
        }
        
        conditions = boundary_manager.get_conditions(context)
        
        # Should find social interaction limits condition
        assert len(conditions) > 0
        social_condition = next(
            (c for c in conditions if c["condition_id"] == "social_interaction_limits"), None
        )
        assert social_condition is not None
        assert social_condition["reason"] == "Maintain appropriate social interaction frequency"
    
    def test_get_policy_hints_external_post(self, boundary_manager):
        """Test getting policy hints for external post context."""
        context = {
            "action_type": "external_post",
            "user_id": "user123",
            "channel": "twitter",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find external post policy hint
        assert len(hints) > 0
        external_post_hint = next(
            (h for h in hints if h["hint_type"] == "wait_for_cooldown"), None
        )
        assert external_post_hint is not None
        assert "cooldown" in external_post_hint["reason"].lower()
    
    def test_get_policy_hints_complex_topic(self, boundary_manager):
        """Test getting policy hints for complex topic context."""
        context = {
            "topic_complexity": "high",
            "audience_expertise": "low",
            "content_length": "long",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find summary policy hint
        assert len(hints) > 0
        summary_hint = next(
            (h for h in hints if h["hint_type"] == "generate_summary_first"), None
        )
        assert summary_hint is not None
        assert "summary" in summary_hint["reason"].lower()
    
    def test_get_policy_hints_high_stress(self, boundary_manager):
        """Test getting policy hints for high stress context."""
        context = {
            "stress_level": "high",
            "decision_impact": "high",
            "time_pressure": "high",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find defer decision policy hint
        assert len(hints) > 0
        defer_hint = next(
            (h for h in hints if h["hint_type"] == "defer_high_impact_decisions"), None
        )
        assert defer_hint is not None
        assert "defer" in defer_hint["reason"].lower()
    
    def test_get_policy_hints_creative_flow(self, boundary_manager):
        """Test getting policy hints for creative flow context."""
        context = {
            "creative_flow": "active",
            "interruption_type": "non_urgent",
            "flow_duration": "recent",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find defer interruption policy hint
        assert len(hints) > 0
        defer_hint = next(
            (h for h in hints if h["hint_type"] == "defer_non_urgent_interruptions"), None
        )
        assert defer_hint is not None
        assert "interruption" in defer_hint["reason"].lower()
    
    def test_get_policy_hints_learning_mode(self, boundary_manager):
        """Test getting policy hints for learning mode context."""
        context = {
            "learning_mode": "active",
            "session_duration": "recent",
            "interruption_type": "distracting",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find continue learning policy hint
        assert len(hints) > 0
        continue_hint = next(
            (h for h in hints if h["hint_type"] == "continue_learning_session"), None
        )
        assert continue_hint is not None
        assert "learning" in continue_hint["reason"].lower()
    
    def test_get_policy_hints_social_interaction(self, boundary_manager):
        """Test getting policy hints for social interaction context."""
        context = {
            "interaction_type": "social",
            "frequency": "high",
            "duration": "extended",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find pace interactions policy hint
        assert len(hints) > 0
        pace_hint = next(
            (h for h in hints if h["hint_type"] == "pace_social_interactions"), None
        )
        assert pace_hint is not None
        assert "social" in pace_hint["reason"].lower()
    
    def test_policy_hint_priority_calculation(self, boundary_manager):
        """Test policy hint priority calculation."""
        context = {
            "decision_impact": "high",
            "urgency": "high",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # High impact and urgency should result in high priority hints
        assert len(hints) > 0
        for hint in hints:
            assert hint["priority"] >= 5  # Base priority
            if "high_impact" in hint["reason"] or "urgent" in hint["reason"]:
                assert hint["priority"] >= 7  # Should be high priority
    
    def test_policy_hint_expiration(self, boundary_manager):
        """Test policy hint expiration calculation."""
        context = {
            "action_type": "external_post",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Hints with cooldowns should have expiration times
        assert len(hints) > 0
        for hint in hints:
            if "cooldown" in hint["reason"].lower():
                assert hint["expires_at"] is not None
                # Expiration should be in the future
                expires_at = datetime.fromisoformat(hint["expires_at"])
                assert expires_at > datetime.utcnow()
    
    def test_global_policy_hints_stress(self, boundary_manager):
        """Test global policy hints for high stress."""
        context = {
            "stress_level": "high",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should include stress management hint
        stress_hint = next(
            (h for h in hints if h["hint_type"] == "stress_management"), None
        )
        assert stress_hint is not None
        assert stress_hint["priority"] >= 7
    
    def test_global_policy_hints_energy(self, boundary_manager):
        """Test global policy hints for low energy."""
        context = {
            "energy_level": "low",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should include energy conservation hint
        energy_hint = next(
            (h for h in hints if h["hint_type"] == "energy_conservation"), None
        )
        assert energy_hint is not None
        assert energy_hint["priority"] >= 6
    
    def test_global_policy_hints_learning(self, boundary_manager):
        """Test global policy hints for learning mode."""
        context = {
            "learning_mode": "active",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should include learning focus hint
        learning_hint = next(
            (h for h in hints if h["hint_type"] == "learning_focus"), None
        )
        assert learning_hint is not None
        assert learning_hint["priority"] >= 8
    
    def test_global_policy_hints_creative_flow(self, boundary_manager):
        """Test global policy hints for creative flow."""
        context = {
            "creative_flow": "active",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Should include creative protection hint
        creative_hint = next(
            (h for h in hints if h["hint_type"] == "creative_protection"), None
        )
        assert creative_hint is not None
        assert creative_hint["priority"] >= 9
    
    def test_cooldown_management(self, boundary_manager):
        """Test cooldown management functionality."""
        context = {
            "action_type": "external_post",
            "user_id": "user123",
        }
        
        # Set a cooldown
        boundary_manager.set_cooldown("external_post_cooldown", context, 600)
        
        # Check that cooldown is active
        required_checks = boundary_manager.check_required_checks("external_post_cooldown", context)
        assert len(required_checks) > 0
        
        # Mark a check as completed
        boundary_manager.mark_check_completed("external_post_cooldown", context, "content_quality")
        
        # Check that the completed check is no longer required
        required_checks = boundary_manager.check_required_checks("external_post_cooldown", context)
        assert "content_quality" not in required_checks
    
    def test_condition_application_logic(self, boundary_manager):
        """Test condition application logic with different context values."""
        # Test with string values
        context_string = {
            "topic_complexity": "high",
            "audience_expertise": "low",
        }
        conditions_string = boundary_manager.get_conditions(context_string)
        assert len(conditions_string) > 0
        
        # Test with numeric values
        context_numeric = {
            "topic_complexity": 0.8,
            "audience_expertise": 0.2,
        }
        conditions_numeric = boundary_manager.get_conditions(context_numeric)
        assert len(conditions_numeric) > 0
        
        # Test with mixed values
        context_mixed = {
            "topic_complexity": "high",
            "audience_expertise": 0.2,
        }
        conditions_mixed = boundary_manager.get_conditions(context_mixed)
        assert len(conditions_mixed) > 0
    
    def test_boundary_summary(self, boundary_manager):
        """Test boundary summary generation."""
        summary = boundary_manager.get_boundary_summary()
        
        assert "active_conditions" in summary
        assert "active_cooldowns" in summary
        assert "condition_types" in summary
        assert "cooldown_types" in summary
        
        assert summary["active_conditions"] > 0
        assert isinstance(summary["condition_types"], list)
        assert isinstance(summary["cooldown_types"], list)
    
    def test_add_remove_conditions(self, boundary_manager):
        """Test adding and removing custom conditions."""
        # Add a custom condition
        custom_condition = BoundaryCondition(
            condition_id="custom_test",
            reason="Test condition for unit testing",
            conditions={"test_param": "test_value"},
            policy_hint="test_hint",
        )
        
        boundary_manager.add_condition(custom_condition)
        
        # Verify condition was added
        context = {"test_param": "test_value"}
        conditions = boundary_manager.get_conditions(context)
        custom_found = next(
            (c for c in conditions if c["condition_id"] == "custom_test"), None
        )
        assert custom_found is not None
        
        # Remove the condition
        boundary_manager.remove_condition("custom_test")
        
        # Verify condition was removed
        conditions = boundary_manager.get_conditions(context)
        custom_found = next(
            (c for c in conditions if c["condition_id"] == "custom_test"), None
        )
        assert custom_found is None
    
    def test_hint_sorting_by_priority(self, boundary_manager):
        """Test that policy hints are sorted by priority."""
        context = {
            "stress_level": "high",
            "decision_impact": "high",
            "urgency": "high",
            "creative_flow": "active",
        }
        
        hints = boundary_manager.get_policy_hints(context)
        
        # Hints should be sorted by priority (highest first)
        priorities = [hint["priority"] for hint in hints]
        assert priorities == sorted(priorities, reverse=True)
    
    def test_multiple_conditions_same_context(self, boundary_manager):
        """Test handling multiple conditions for the same context."""
        context = {
            "stress_level": "high",
            "decision_impact": "high",
            "time_pressure": "high",
            "creative_flow": "active",
            "interruption_type": "non_urgent",
        }
        
        conditions = boundary_manager.get_conditions(context)
        hints = boundary_manager.get_policy_hints(context)
        
        # Should find multiple conditions and hints
        assert len(conditions) >= 2
        assert len(hints) >= 2
        
        # Should include both stress protection and creative flow protection
        condition_ids = [c["condition_id"] for c in conditions]
        assert "high_stress_protection" in condition_ids
        assert "creative_flow_protection" in condition_ids