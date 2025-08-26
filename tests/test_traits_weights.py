"""
Tests for trait weights functionality.

This module tests the trait weight resolution and adjustment logic.
"""

import pytest
from datetime import datetime

from pmx.matrix import PersonalityMatrix
from pmx.models import PMXConfig, TraitWeights, AffectSnapshot


class TestTraitWeights:
    """Test trait weight resolution and adjustments."""
    
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
    def pmx(self, config):
        """Create a Personality Matrix instance."""
        return PersonalityMatrix(config)
    
    def test_resolve_weights_baseline(self, pmx):
        """Test baseline weight resolution."""
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # Check that all weights are present
        assert hasattr(weights, "creative")
        assert hasattr(weights, "analytical")
        assert hasattr(weights, "empathic")
        assert hasattr(weights, "curiosity")
        assert hasattr(weights, "balance")
        
        # Check that weights are normalized
        assert 0.1 <= weights.creative <= 1.0
        assert 0.1 <= weights.analytical <= 1.0
        assert 0.1 <= weights.empathic <= 1.0
        assert 0.1 <= weights.curiosity <= 1.0
        assert 0.1 <= weights.balance <= 1.0
    
    def test_resolve_weights_creative_task(self, pmx):
        """Test weight resolution for creative tasks."""
        context = {"task_type": "creative"}
        weights = pmx.resolve_weights(context)
        
        # Creative tasks should boost creative and curiosity weights
        assert weights.creative > 0.5
        assert weights.curiosity > 0.5
    
    def test_resolve_weights_analytical_task(self, pmx):
        """Test weight resolution for analytical tasks."""
        context = {"task_type": "analytical"}
        weights = pmx.resolve_weights(context)
        
        # Analytical tasks should boost analytical and balance weights
        assert weights.analytical > 0.5
        assert weights.balance > 0.5
    
    def test_resolve_weights_social_task(self, pmx):
        """Test weight resolution for social tasks."""
        context = {"task_type": "social"}
        weights = pmx.resolve_weights(context)
        
        # Social tasks should boost empathic and curiosity weights
        assert weights.empathic > 0.5
        assert weights.curiosity > 0.5
    
    def test_resolve_weights_audience_friend(self, pmx):
        """Test weight resolution for friend audience."""
        context = {"audience": "friend"}
        weights = pmx.resolve_weights(context)
        
        # Friend audience should boost empathic and creative weights
        assert weights.empathic > 0.5
        assert weights.creative > 0.5
    
    def test_resolve_weights_audience_professional(self, pmx):
        """Test weight resolution for professional audience."""
        context = {"audience": "professional"}
        weights = pmx.resolve_weights(context)
        
        # Professional audience should boost analytical and balance weights
        assert weights.analytical > 0.5
        assert weights.balance > 0.5
    
    def test_resolve_weights_audience_child(self, pmx):
        """Test weight resolution for child audience."""
        context = {"audience": "child"}
        weights = pmx.resolve_weights(context)
        
        # Child audience should boost empathic, creative, and curiosity weights
        assert weights.empathic > 0.5
        assert weights.creative > 0.5
        assert weights.curiosity > 0.5
    
    def test_resolve_weights_high_urgency(self, pmx):
        """Test weight resolution for high urgency."""
        context = {"urgency": "high"}
        weights = pmx.resolve_weights(context)
        
        # High urgency should boost analytical and balance weights
        assert weights.analytical > 0.5
        assert weights.balance > 0.5
    
    def test_resolve_weights_low_urgency(self, pmx):
        """Test weight resolution for low urgency."""
        context = {"urgency": "low"}
        weights = pmx.resolve_weights(context)
        
        # Low urgency should boost creative and curiosity weights
        assert weights.creative > 0.5
        assert weights.curiosity > 0.5
    
    def test_affect_adjustments_high_arousal(self, pmx):
        """Test affect adjustments for high arousal."""
        # Set high arousal affect
        affect = AffectSnapshot(
            arousal=0.8,
            valence=0.5,
            stress=0.3,
            tags=["excited"],
        )
        pmx.update_affect(affect)
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # High arousal should boost creative and curiosity weights
        assert weights.creative > 0.5
        assert weights.curiosity > 0.5
    
    def test_affect_adjustments_low_arousal(self, pmx):
        """Test affect adjustments for low arousal."""
        # Set low arousal affect
        affect = AffectSnapshot(
            arousal=0.2,
            valence=0.3,
            stress=0.2,
            tags=["calm"],
        )
        pmx.update_affect(affect)
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # Low arousal should boost analytical and balance weights
        assert weights.analytical > 0.5
        assert weights.balance > 0.5
    
    def test_affect_adjustments_high_stress(self, pmx):
        """Test affect adjustments for high stress."""
        # Set high stress affect
        affect = AffectSnapshot(
            arousal=0.6,
            valence=-0.2,
            stress=0.8,
            tags=["stressed"],
        )
        pmx.update_affect(affect)
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # High stress should boost analytical weight and reduce creative weight
        assert weights.analytical > 0.5
        assert weights.creative < 0.6
    
    def test_affect_adjustments_positive_valence(self, pmx):
        """Test affect adjustments for positive valence."""
        # Set positive valence affect
        affect = AffectSnapshot(
            arousal=0.5,
            valence=0.7,
            stress=0.2,
            tags=["positive"],
        )
        pmx.update_affect(affect)
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # Positive valence should boost empathic and creative weights
        assert weights.empathic > 0.5
        assert weights.creative > 0.5
    
    def test_affect_adjustments_negative_valence(self, pmx):
        """Test affect adjustments for negative valence."""
        # Set negative valence affect
        affect = AffectSnapshot(
            arousal=0.4,
            valence=-0.6,
            stress=0.3,
            tags=["negative"],
        )
        pmx.update_affect(affect)
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # Negative valence should boost analytical weight and reduce empathic weight
        assert weights.analytical > 0.5
        assert weights.empathic < 0.6
    
    def test_trait_adjustments_high_creative_trait(self, pmx):
        """Test trait adjustments for high creative trait."""
        # Set high creative trait
        pmx.traits.creative = 0.9
        pmx.traits.analytical = 0.3
        pmx.traits.empathic = 0.5
        pmx.traits.curiosity = 0.7
        pmx.traits.balance = 0.4
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # High creative trait should boost creative weight
        assert weights.creative > 0.6
    
    def test_trait_adjustments_high_analytical_trait(self, pmx):
        """Test trait adjustments for high analytical trait."""
        # Set high analytical trait
        pmx.traits.creative = 0.3
        pmx.traits.analytical = 0.9
        pmx.traits.empathic = 0.5
        pmx.traits.curiosity = 0.4
        pmx.traits.balance = 0.7
        
        context = {"task_type": "general"}
        weights = pmx.resolve_weights(context)
        
        # High analytical trait should boost analytical weight
        assert weights.analytical > 0.6
    
    def test_weight_normalization(self, pmx):
        """Test that weights are properly normalized."""
        # Create a context that would push weights very high
        context = {
            "task_type": "creative",
            "audience": "child",
            "urgency": "low",
        }
        
        # Set high affect values
        affect = AffectSnapshot(
            arousal=0.9,
            valence=0.8,
            stress=0.1,
            tags=["excited", "positive"],
        )
        pmx.update_affect(affect)
        
        weights = pmx.resolve_weights(context)
        
        # Check that no weight exceeds 1.0
        assert weights.creative <= 1.0
        assert weights.analytical <= 1.0
        assert weights.empathic <= 1.0
        assert weights.curiosity <= 1.0
        assert weights.balance <= 1.0
        
        # Check that all weights have minimum values
        assert weights.creative >= 0.1
        assert weights.analytical >= 0.1
        assert weights.empathic >= 0.1
        assert weights.curiosity >= 0.1
        assert weights.balance >= 0.1
    
    def test_complex_context_combination(self, pmx):
        """Test weight resolution with complex context combination."""
        context = {
            "task_type": "problem_solving",
            "audience": "professional",
            "urgency": "high",
        }
        
        # Set moderate affect
        affect = AffectSnapshot(
            arousal=0.5,
            valence=0.0,
            stress=0.4,
            tags=["focused"],
        )
        pmx.update_affect(affect)
        
        weights = pmx.resolve_weights(context)
        
        # Problem solving + professional + high urgency should favor analytical
        assert weights.analytical > weights.creative
        assert weights.analytical > weights.empathic
        assert weights.balance > 0.4  # Balance should be moderate
    
    def test_weight_consistency(self, pmx):
        """Test that weights are consistent for the same context."""
        context = {"task_type": "analytical", "audience": "professional"}
        
        weights1 = pmx.resolve_weights(context)
        weights2 = pmx.resolve_weights(context)
        
        # Weights should be consistent (within small floating point differences)
        assert abs(weights1.creative - weights2.creative) < 0.001
        assert abs(weights1.analytical - weights2.analytical) < 0.001
        assert abs(weights1.empathic - weights2.empathic) < 0.001
        assert abs(weights1.curiosity - weights2.curiosity) < 0.001
        assert abs(weights1.balance - weights2.balance) < 0.001